import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load .env file if it exists (for local development), but don't fail if it doesn't
load_dotenv()

# â”€â”€ Startup env validation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_REQUIRED = ["GROQ_API_KEY", "JWT_SECRET", "MONGO_URL"]
_missing = [k for k in _REQUIRED if not os.environ.get(k)]
if _missing:
    print(f"WARNING: Missing env vars: {', '.join(_missing)}. Some features may not work.")
    print(f"Debug info - GROQ_API_KEY present: {bool(os.environ.get('GROQ_API_KEY'))}")

from routes.auth_routes import router as auth_router
from routes.recipe_routes import router as recipe_router
from routes.ai_routes import router as ai_router
from routes.pantry_routes import router as pantry_router
from routes.nutrition_routes import router as nutrition_router
from routes.meal_plan_routes import router as meal_plan_router
from routes.dish_routes import router as dish_router
from routes.moderation_routes import router as moderation_router
from routes.upload_routes import router as upload_router
from routes.collections_routes import router as collections_router
from database import recipes, dishes, recipe_variations, collections


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Create indexes with error handling
        try:
            await recipes.create_index([("name", "text"), ("description", "text"), ("nationality", "text")])
        except Exception:
            pass  # Index may already exist
        
        try:
            await recipes.create_index("nationality")
        except Exception:
            pass
        
        try:
            await recipes.create_index("created_at")
        except Exception:
            pass
        
        try:
            await dishes.create_index([("name", "text"), ("name_amharic", "text"), ("category", "text")])
        except Exception:
            pass
        
        try:
            await dishes.create_index("slug", unique=True)
        except Exception:
            pass
        
        try:
            await recipe_variations.create_index([("ingredients", "text"), ("notes", "text")])
        except Exception:
            pass
        
        try:
            await recipe_variations.create_index("dish_id")
        except Exception:
            pass
        
        try:
            await recipe_variations.create_index("dietary_tags")
        except Exception:
            pass
        
        try:
            await collections.create_index("slug", unique=True)
        except Exception:
            pass
        
        yield
    except Exception as e:
        # Log the error but don't fail startup
        print(f"Warning: Index creation failed: {e}")
        yield


app = FastAPI(title="Megeb API", lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,https://megeb.vercel.app,https://megeb.onrender.com").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "message": exc.detail, "code": f"HTTP_{exc.status_code}"},
        )
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal server error", "code": "INTERNAL_ERROR"},
    )


@app.middleware("http")
async def block_sensitive_paths(request: Request, call_next):
    path = request.url.path.lower()
    if path.startswith("/backend") or path.endswith(".env") or "/.env" in path:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return await call_next(request)


app.include_router(auth_router)
app.include_router(recipe_router)
app.include_router(ai_router)
app.include_router(pantry_router)
app.include_router(nutrition_router)
app.include_router(meal_plan_router)
app.include_router(dish_router)
app.include_router(moderation_router)
app.include_router(upload_router)
app.include_router(collections_router)


@app.get("/")
def index():
    return {"status": "ok", "service": "Megeb API"}

@app.get("/api")
def root():
    return {"status": "Megeb API running"}

@app.get("/health")
async def health():
    try:
        await dishes.find_one({})
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "db": db_ok}


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (remove in production)"""
    return {
        "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
        "groq_api_key_length": len(os.getenv("GROQ_API_KEY", "")),
        "mongo_url_set": bool(os.getenv("MONGO_URL")),
        "jwt_secret_set": bool(os.getenv("JWT_SECRET")),
        "cors_origins": os.getenv("CORS_ORIGINS", "not set"),
    }


uploads_path = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")



@app.post("/internal/seed-recipes")
async def seed_recipes_endpoint(secret: str):
    if secret != "megeb-seed-2024":
        raise HTTPException(status_code=403, detail="Forbidden")
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, "seed_recipes.py"],
        capture_output=True, text=True, cwd="/app"
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


@app.post("/internal/fix-images")
async def fix_images_endpoint(secret: str):
    """Give every dish its own real, working photo.

    The old version of this endpoint hardcoded a name -> URL dict. That's why
    it kept failing: most of those URLs were guessed Wikimedia file paths that
    don't actually exist, and dozens of unrelated dishes were pointed at the
    exact same fallback image on purpose, so "every dish has its own image"
    was never actually true.

    This version doesn't guess or hardcode a single URL. For every dish
    currently in the database it asks Wikipedia's live search API for
    real pages about that dish and takes the current image straight from
    Wikipedia's own CDN, so a link can't go stale or 404 the way a
    hand-typed one can. Candidates are then handed out so no two dishes
    ever end up with the same picture.
    """
    if secret != "megeb-seed-2024":
        raise HTTPException(status_code=403, detail="Forbidden")

    import asyncio
    import httpx

    WIKI_API = "https://en.wikipedia.org/w/api.php"
    HEADERS = {"User-Agent": "MegebEthiopianFoodApp/1.0 (https://megeb.vercel.app)"}
    sem = asyncio.Semaphore(10)

    async def search_images(client: httpx.AsyncClient, query: str, limit: int = 6):
        """Real, live results only — nothing here is a hand-typed guess."""
        if not query.strip():
            return []
        try:
            async with sem:
                resp = await client.get(
                    WIKI_API,
                    params={
                        "action": "query",
                        "generator": "search",
                        "gsrsearch": query,
                        "gsrlimit": limit,
                        "gsrnamespace": 0,
                        "prop": "pageimages",
                        "piprop": "thumbnail",
                        "pithumbsize": 800,
                        "format": "json",
                    },
                    headers=HEADERS,
                    timeout=10.0,
                )
            data = resp.json()
            pages = list(data.get("query", {}).get("pages", {}).values())
            pages.sort(key=lambda p: p.get("index", 999))
            return [
                p["thumbnail"]["source"]
                for p in pages
                if p.get("thumbnail", {}).get("source")
            ]
        except Exception:
            return []

    async def resolve(client: httpx.AsyncClient, dish_doc: dict):
        name = dish_doc.get("name", "")
        name_am = dish_doc.get("name_amharic", "")
        candidates = await search_images(client, f"{name} Ethiopian dish food")
        if len(candidates) < 3:
            candidates += await search_images(client, f"{name} Ethiopia")
        if len(candidates) < 3 and name_am:
            candidates += await search_images(client, name_am)
        # de-dupe while preserving relevance order
        seen = set()
        ordered = [c for c in candidates if not (c in seen or seen.add(c))]
        return dish_doc["_id"], name, ordered

    async with httpx.AsyncClient() as client:
        all_dishes = await dishes.find({}).to_list(length=None)
        results = await asyncio.gather(*[resolve(client, d) for d in all_dishes])

    # Greedily hand out the best still-unused photo to each dish, in the same
    # order dishes were created, so no two dishes ever share an image.
    used = set()
    updated = 0
    unresolved = []
    for dish_id, name, candidates in results:
        chosen = next((u for u in candidates if u not in used), None)
        if chosen:
            used.add(chosen)
            await dishes.update_one({"_id": dish_id}, {"$set": {"reference_image_url": chosen}})
            updated += 1
        else:
            unresolved.append(name)

    return {
        "total_dishes": len(all_dishes),
        "updated": updated,
        "unique_images_assigned": len(used),
        "unresolved": unresolved,
    }
