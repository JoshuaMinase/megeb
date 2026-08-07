from fastapi import APIRouter, Depends, HTTPException, Query
from models.schemas import RecipeCreate
from database import recipes, searches
from auth import get_current_user, optional_user
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _out(r: dict) -> dict:
    out = dict(r)
    out["id"] = str(out.pop("_id"))
    return out


# ── GET /recipes/trending  (must be before /:id) ──────────────────────────────
@router.get("/trending")
async def trending(limit: int = Query(10, le=50)):
    """Most-searched recipes by search log count."""
    pipeline = [
        {"$group": {"_id": "$recipe_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$lookup": {"from": "recipes", "localField": "_id", "foreignField": "_id", "as": "recipe"}},
        {"$unwind": "$recipe"},
        {"$replaceRoot": {"newRoot": "$recipe"}},
    ]
    docs = await searches.aggregate(pipeline).to_list(limit)
    if not docs:
        docs = await recipes.find().sort("created_at", -1).limit(limit).to_list(limit)
    return [_out(d) for d in docs]


# ── GET /recipes  (paginated, personalised) ────────────────────────────────────
@router.get("/")
async def list_recipes(
    page: int = Query(1, ge=1),
    limit: int = Query(12, le=50),
    user=Depends(optional_user),
):
    skip = (page - 1) * limit
    query = {}

    # personalise: show nationality-matching food first via sort trick
    if user:
        nat = user.get("nationality", "")
        # MongoDB: docs matching nationality come first (score 1 vs 0)
        pipeline = [
            {"$addFields": {"_score": {"$cond": [{"$eq": ["$nationality", nat]}, 1, 0]}}},
            {"$sort": {"_score": -1, "created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
        ]
        docs = await recipes.aggregate(pipeline).to_list(limit)
    else:
        docs = await recipes.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    total = await recipes.count_documents(query)
    return {"recipes": [_out(d) for d in docs], "total": total, "page": page, "limit": limit}


# ── POST /recipes ──────────────────────────────────────────────────────────────
@router.post("/", status_code=201)
async def create_recipe(body: RecipeCreate, user=Depends(get_current_user)):
    doc = body.model_dump()
    doc["nationality"]  = (doc.get("nationality") or "Ethiopian").strip() or "Ethiopian"
    doc["author_id"]   = str(user["_id"])
    doc["author_name"] = user["name"]
    doc["created_at"]  = datetime.now(timezone.utc)
    doc["search_count"] = 0
    result = await recipes.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _out(doc)


# ── GET /recipes/search?q= ─────────────────────────────────────────────────────
@router.get("/search/q")
async def search_recipes(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(12, le=50),
    user=Depends(optional_user),
):
    skip  = (page - 1) * limit
    query = {"$text": {"$search": q}}

    docs  = await recipes.find(query).skip(skip).limit(limit).to_list(limit)
    total = await recipes.count_documents(query)

    # log search for trending — store recipe_id as ObjectId for consistent lookup
    if docs:
        log_entries = [
            {"query": q, "recipe_id": d["_id"],
             "user_id": str(user["_id"]) if user else None,
             "at": datetime.now(timezone.utc)}
            for d in docs
        ]
        await searches.insert_many(log_entries)

    return {"recipes": [_out(d) for d in docs], "total": total, "page": page, "limit": limit}


# ── GET /recipes/:id ───────────────────────────────────────────────────────────
@router.get("/{recipe_id}")
async def get_recipe(recipe_id: str):
    if not ObjectId.is_valid(recipe_id):
        raise HTTPException(status_code=404, detail="Not found")
    oid    = ObjectId(recipe_id)
    recipe = await recipes.find_one({"_id": oid})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    await recipes.update_one({"_id": oid}, {"$inc": {"search_count": 1}})
    return _out(recipe)
