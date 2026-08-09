"""
RAG indexing script for the Gursha cookbook.

Reads the extracted epub HTML chapters, splits them into text chunks,
and stores them in a MongoDB `rag_chunks` collection.

The AI endpoint queries this collection using a simple keyword/regex search
to inject relevant cookbook context before calling Groq.

Usage:
    python rag_index.py

Requirements:
    - epub must already be extracted to epub_extracted/ (run once)
    - MONGO_URL must be set in backend/.env
"""

import asyncio
import os
import re
from html.parser import HTMLParser
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  # tries backend/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))  # fallback to root .env

_mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
if "mongodb+srv://" in _mongo_url:
    client = AsyncIOMotorClient(
        _mongo_url,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
    )
else:
    client = AsyncIOMotorClient(_mongo_url)
db = client[os.getenv("DB_NAME", "megeb")]
rag_col = db["rag_chunks"]

# Path to extracted epub (relative to backend/ or absolute)
EPUB_DIR = os.path.join(os.path.dirname(__file__), "..", "epub_extracted", "OEBPS", "xhtml")

# Chapters to index with their friendly names
CHAPTERS = [
    ("010_c001_Chapter_1_Makeda_s_K.xhtml", "Makeda's Kitchen — Spice Blends & Bases"),
    ("011_c002_Chapter_2_Bread.xhtml",       "Bread"),
    ("012_c003_Chapter_3_Sunrise_Su.xhtml",  "Sunrise Sustenance — Breakfast"),
    ("013_c004_Chapter_4_Vegetables.xhtml",  "Vegetables"),
    ("014_c005_Chapter_5_Legumes_an.xhtml",  "Legumes and Grains"),
    ("015_c006_Chapter_6_Meat_and_F.xhtml",  "Meat and Fish"),
    ("009_in_Introduction.xhtml",            "Introduction — Author's Story"),
]

# Chunk size in characters (target ~500 chars per chunk)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


# ── HTML to plain text ────────────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip_tags = {"script", "style"}
        self._in_skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._in_skip += 1

    def handle_endtag(self, tag):
        if tag in self._skip_tags and self._in_skip:
            self._in_skip -= 1

    def handle_data(self, data):
        if not self._in_skip:
            text = data.strip()
            if text:
                self.parts.append(text)


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    text = " ".join(parser.parts)
    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Fix encoding artefacts common in epub files
    text = text.replace("\u00e2\u0080\u0099", "'").replace("\u00e2\u0080\u009c", '"').replace("\u00e2\u0080\u009d", '"')
    text = text.replace("\u00c2\u00bd", "\u00bd").replace("\u00c2\u00bc", "\u00bc").replace("\u00c2\u00be", "\u00be")
    text = text.replace("\u00c2\u00b0", "\u00b0").replace("\u00e2\u0080\u0094", "\u2014").replace("\u00e2\u0080\u0093", "\u2013")
    text = text.replace("\u00c3\u00a9", "\u00e9").replace("\u00e2\u0080\u00a6", "...")
    return text


# ── Chunking ──────────────────────────────────────────────────────────────────

def split_into_chunks(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks, preferring sentence boundaries."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        # Try to break at a sentence boundary (period + space)
        boundary = text.rfind(". ", start, end)
        if boundary == -1 or boundary <= start:
            boundary = end
        else:
            boundary += 1  # include the period
        chunk = text[start:boundary].strip()
        if chunk:
            chunks.append(chunk)
        start = max(start + 1, boundary - overlap)
    return [c for c in chunks if len(c) > 40]  # drop tiny fragments


# ── Extract recipe title from surrounding text ─────────────────────────────────

def _extract_recipe_hint(chunk: str) -> str:
    """Try to pull a recipe name from a chunk for better searchability."""
    # Look for patterns like "Dish Name\nSubtitle" near the start of the chunk
    match = re.match(r"^([A-Z][^\n.]{3,60})", chunk)
    if match:
        return match.group(1).strip()
    return ""


# ── Main indexer ──────────────────────────────────────────────────────────────

async def index(force: bool = False):
    now = datetime.now(timezone.utc)

    print(">> Checking for existing RAG index...")
    existing_count = await rag_col.count_documents({})
    if existing_count > 0:
        if not force:
            print(f"  RAG index already contains {existing_count} chunks.")
            print("  Skipping re-index. Use --force to rebuild.")
            client.close()
            return
        print(f"  Found {existing_count} existing chunks. Dropping and re-indexing...")
        await rag_col.drop()

    total_chunks = 0

    for filename, chapter_name in CHAPTERS:
        filepath = os.path.join(EPUB_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  [WARN]  File not found, skipping: {filepath}")
            continue

        print(f"  [CH] Indexing: {chapter_name}")

        with open(filepath, encoding="utf-8", errors="replace") as f:
            html = f.read()

        text = html_to_text(html)
        chunks = split_into_chunks(text)

        docs = []
        for i, chunk in enumerate(chunks):
            docs.append({
                "chapter": chapter_name,
                "filename": filename,
                "chunk_index": i,
                "text": chunk,
                "recipe_hint": _extract_recipe_hint(chunk),
                "created_at": now,
            })

        if docs:
            # Insert in small batches to avoid Atlas timeout on free tier
            batch_size = 50
            for i in range(0, len(docs), batch_size):
                await rag_col.insert_many(docs[i:i + batch_size])
            total_chunks += len(docs)
            print(f"     -> {len(docs)} chunks")

    # Create a text index for keyword search
    await rag_col.create_index([("text", "text"), ("chapter", "text")])
    print(f"\n[OK] RAG index created: {total_chunks} chunks across {len(CHAPTERS)} chapters.")
    print("   Text search index created on `rag_chunks` collection.")
    client.close()


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    asyncio.run(index(force=force))
