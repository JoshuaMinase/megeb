from fastapi import APIRouter, Depends, HTTPException, Query
from models.schemas import DishCreate, VariationCreate, DIETARY_TAGS
from database import dishes, recipe_variations, searches
from auth import get_current_user
from bson import ObjectId
from datetime import datetime, timezone
import bleach
import math

router = APIRouter(prefix="/api/dishes", tags=["dishes"])


def _sanitize(text: str, max_length: int = 500) -> str:
    return bleach.clean(text, tags=[], strip=True)[:max_length] if text else ""


def _dish_out(d: dict) -> dict:
    out = dict(d)
    out["id"] = str(out.pop("_id"))
    return out


def _var_out(v: dict) -> dict:
    out = dict(v)
    out["id"] = str(out.pop("_id"))
    out["dish_id"] = str(out.get("dish_id", ""))
    return out


@router.get("/trending")
async def trending_dishes(limit: int = Query(8, le=20)):
    pipeline = [
        {"$group": {"_id": "$dish_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit * 2},  # over-fetch to account for non-approved dishes
        {
            "$lookup": {
                "from": "dishes",
                "let": {"did": "$_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$or": [
                        {"$eq": ["$_id", "$$did"]},
                        {"$eq": [{"$toString": "$_id"}, {"$toString": "$$did"}]},
                    ]}}},
                ],
                "as": "dish",
            }
        },
        {"$unwind": {"path": "$dish", "preserveNullAndEmptyArrays": False}},
        {"$match": {"dish.status": "approved"}},
        {"$replaceRoot": {"newRoot": "$dish"}},
        {"$limit": limit},
    ]
    docs = await searches.aggregate(pipeline).to_list(limit)
    if not docs:
        docs = await dishes.find({"status": "approved"}).sort("variation_count", -1).limit(limit).to_list(limit)
    return [_dish_out(d) for d in docs]


@router.get("")
async def list_dishes(
    category: str = Query(None),
    search: str = Query(None),
    diet: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(12, le=50),
):
    query = {"status": "approved"}
    if category:
        query["category"] = category
    if search:
        query["$text"] = {"$search": search}

    # Diet filter: find dish_ids that have at least one approved variation with all requested tags
    if diet:
        tags = [t.strip() for t in diet.split(",") if t.strip() in DIETARY_TAGS]
        if tags:
            matching_vars = await recipe_variations.distinct(
                "dish_id",
                {"status": "approved", "dietary_tags": {"$all": tags}},
            )
            # distinct returns a mix of ObjectId and str — normalise to ObjectId only
            oid_set = set()
            for did in matching_vars:
                s = str(did)
                if ObjectId.is_valid(s):
                    oid_set.add(ObjectId(s))
            query["_id"] = {"$in": list(oid_set)}

    skip = (page - 1) * limit
    total = await dishes.count_documents(query)
    cursor = dishes.find(query).sort("variation_count", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)

    # Compute top_tags: for each dish, find the union of dietary_tags across approved variations
    if docs:
        dish_ids_str = [str(d["_id"]) for d in docs]
        # Query variations matching by both str and ObjectId dish_id
        tags_cursor = recipe_variations.find(
            {"$or": [
                {"dish_id": {"$in": dish_ids_str}},
                {"dish_id": {"$in": [d["_id"] for d in docs]}},
            ], "status": "approved", "dietary_tags": {"$exists": True, "$ne": []}},
            {"dish_id": 1, "dietary_tags": 1},
        )
        tags_by_dish: dict = {}
        async for v in tags_cursor:
            key = str(v["dish_id"])
            if key not in tags_by_dish:
                tags_by_dish[key] = {}
            for t in (v.get("dietary_tags") or []):
                tags_by_dish[key][t] = tags_by_dish[key].get(t, 0) + 1
        # Attach sorted top_tags (up to 3 most common) to each dish doc
        for d in docs:
            counts = tags_by_dish.get(str(d["_id"]), {})
            d["top_tags"] = sorted(counts, key=counts.get, reverse=True)[:3]

    return {
        "dishes": [_dish_out(d) for d in docs],
        "total": total,
        "page": page,
        "pages": math.ceil(total / limit) if total else 1,
    }


@router.get("/{slug}/variations/{variation_id}")
async def get_variation(slug: str, variation_id: str):
    if not ObjectId.is_valid(variation_id):
        raise HTTPException(status_code=400, detail="Invalid variation id")
    variation = await recipe_variations.find_one({"_id": ObjectId(variation_id), "status": "approved"})
    if not variation:
        raise HTTPException(status_code=404, detail="Variation not found")
    return _var_out(variation)


@router.get("/{slug}")
async def get_dish(slug: str):
    dish = await dishes.find_one({"slug": slug, "status": "approved"})
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    await dishes.update_one({"_id": dish["_id"]}, {"$inc": {"search_count": 1}})
    await searches.insert_one({"dish_id": dish["_id"], "at": datetime.now(timezone.utc)})

    # Support both ObjectId and str dish_id for backwards-compat
    variations = await recipe_variations.find(
        {"$or": [{"dish_id": dish["_id"]}, {"dish_id": str(dish["_id"])}], "status": "approved"}
    ).to_list(50)
    return {**_dish_out(dish), "variations": [_var_out(v) for v in variations]}


@router.post("", status_code=201)
async def create_dish(body: DishCreate, user=Depends(get_current_user)):
    slug = _sanitize(body.name, 100).lower().replace(" ", "-").replace("/", "-")
    if await dishes.find_one({"slug": slug}):
        raise HTTPException(status_code=400, detail="Dish already exists")

    doc = {
        "slug": slug,
        "name": _sanitize(body.name, 100),
        "name_amharic": _sanitize(body.name_amharic, 100) if body.name_amharic else "",
        "category": _sanitize(body.category, 50) if body.category else "",
        "region": _sanitize(body.region, 50) if body.region else "",
        "description": _sanitize(body.description, 500),
        "reference_image_url": body.reference_image_url or "",
        "phonetic_name": _sanitize(body.phonetic_name, 100) if body.phonetic_name else "",
        "pronunciation_audio_url": "",
        "status": "pending",
        "submitted_by": str(user["_id"]),
        "variation_count": 0,
        "search_count": 0,
        "created_at": datetime.now(timezone.utc),
    }
    result = await dishes.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _dish_out(doc)


@router.post("/{slug}/variations", status_code=201)
async def create_variation(slug: str, body: VariationCreate, user=Depends(get_current_user)):
    dish = await dishes.find_one({"slug": slug, "status": "approved"})
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    # Validate and filter dietary tags
    valid_tags = [t for t in (body.dietary_tags or []) if t in DIETARY_TAGS]

    doc = {
        "dish_id": str(dish["_id"]),
        "variation_name": _sanitize(body.variation_name, 100),
        "author_id": str(user["_id"]),
        "author_name": user.get("name", ""),
        "ingredients": [bleach.clean(i, tags=[], strip=True)[:200] for i in (body.ingredients or [])],
        "steps": [
            {
                "title": bleach.clean(str(s.get("title", "")), tags=[], strip=True)[:100],
                "text": bleach.clean(str(s.get("text", "")), tags=[], strip=True)[:500],
            }
            for s in (body.steps or [])
        ],
        "image_url": body.image_url or "",
        "prep_time_minutes": body.prep_time_minutes or 0,
        "cook_time_minutes": body.cook_time_minutes or 0,
        "servings": body.servings or 2,
        "spice_level": body.spice_level or "medium",
        "notes": bleach.clean(body.notes or "", tags=[], strip=True)[:500],
        "dietary_tags": valid_tags,
        "story": bleach.clean(body.story or "", tags=[], strip=True)[:1000],
        "status": "pending",
        "likes_count": 0,
        "search_count": 0,
        "created_at": datetime.now(timezone.utc),
    }
    result = await recipe_variations.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _var_out(doc)
