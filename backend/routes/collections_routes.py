from fastapi import APIRouter, Depends, HTTPException
from models.schemas import CollectionCreate, CollectionUpdate
from database import collections
from auth import get_current_user
from bson import ObjectId
from datetime import datetime, timezone
import bleach
import re

router = APIRouter(tags=["collections"])


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", bleach.clean(text, tags=[], strip=True).lower().strip())[:80].strip("-")


def _out(doc: dict) -> dict:
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    return out


async def _admin_only(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ── Admin CRUD ────────────────────────────────────────────────────────────────

@router.post("/api/admin/collections", status_code=201)
async def create_collection(body: CollectionCreate, admin=Depends(_admin_only)):
    slug = _slugify(body.title)
    if not slug:
        raise HTTPException(status_code=400, detail="Invalid title")
    if await collections.find_one({"slug": slug}):
        raise HTTPException(status_code=400, detail="Collection slug already exists")

    doc = {
        "slug": slug,
        "title": bleach.clean(body.title, tags=[], strip=True)[:100],
        "description": bleach.clean(body.description or "", tags=[], strip=True)[:500],
        "cover_image_url": body.cover_image_url or "",
        "dish_ids": body.dish_ids or [],
        "is_active": body.is_active if body.is_active is not None else True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await collections.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _out(doc)


@router.patch("/api/admin/collections/{collection_id}")
async def update_collection(collection_id: str, body: CollectionUpdate, admin=Depends(_admin_only)):
    if not ObjectId.is_valid(collection_id):
        raise HTTPException(status_code=400, detail="Invalid collection id")

    updates = {}
    if body.title is not None:
        updates["title"] = bleach.clean(body.title, tags=[], strip=True)[:100]
    if body.description is not None:
        updates["description"] = bleach.clean(body.description, tags=[], strip=True)[:500]
    if body.cover_image_url is not None:
        updates["cover_image_url"] = body.cover_image_url
    if body.dish_ids is not None:
        updates["dish_ids"] = body.dish_ids
    if body.is_active is not None:
        updates["is_active"] = body.is_active

    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")

    result = await collections.update_one({"_id": ObjectId(collection_id)}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Collection not found")
    doc = await collections.find_one({"_id": ObjectId(collection_id)})
    return _out(doc)


# ── Public ────────────────────────────────────────────────────────────────────

@router.get("/api/collections")
async def list_collections():
    docs = await collections.find({"is_active": True}).sort("created_at", -1).to_list(50)
    return [_out(d) for d in docs]


@router.get("/api/collections/{slug}")
async def get_collection(slug: str):
    doc = await collections.find_one({"slug": slug, "is_active": True})
    if not doc:
        raise HTTPException(status_code=404, detail="Collection not found")
    return _out(doc)
