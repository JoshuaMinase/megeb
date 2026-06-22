from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import get_current_user
from database import dishes, recipe_variations, users
from bson import ObjectId

router = APIRouter(tags=["moderation"])


class ModerationBody(BaseModel):
    action: str  # "approve" | "reject"


async def _admin_only(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def _dish_out(d: dict) -> dict:
    out = dict(d)
    out["id"] = str(out.pop("_id"))
    return out


def _var_out(v: dict) -> dict:
    out = dict(v)
    out["id"] = str(out.pop("_id"))
    return out


def _badge(dishes_count: int, variations_count: int) -> str:
    total = dishes_count + variations_count
    if total >= 15:
        return "Top Contributor"
    if total >= 5:
        return "Regular"
    if total >= 1:
        return "Contributor"
    return ""


@router.get("/api/moderation/queue")
async def moderation_queue(admin=Depends(_admin_only)):
    pending_dishes = await dishes.find({"status": "pending"}).to_list(100)
    pending_variations = await recipe_variations.find({"status": "pending"}).to_list(100)
    return {
        "dishes": [_dish_out(d) for d in pending_dishes],
        "variations": [_var_out(v) for v in pending_variations],
    }


@router.patch("/api/moderation/dishes/{dish_id}")
async def moderate_dish(dish_id: str, body: ModerationBody, admin=Depends(_admin_only)):
    if body.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(status_code=400, detail="Invalid dish id")

    dish = await dishes.find_one({"_id": ObjectId(dish_id)})
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    new_status = "approved" if body.action == "approve" else "rejected"
    await dishes.update_one({"_id": ObjectId(dish_id)}, {"$set": {"status": new_status}})

    if body.action == "approve" and dish.get("submitted_by"):
        submitter_id = dish["submitted_by"]
        if ObjectId.is_valid(submitter_id):
            await users.update_one(
                {"_id": ObjectId(submitter_id)},
                {"$inc": {"dishes_approved_count": 1}},
            )

    return {"id": dish_id, "status": new_status}


@router.patch("/api/moderation/variations/{variation_id}")
async def moderate_variation(variation_id: str, body: ModerationBody, admin=Depends(_admin_only)):
    if body.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
    if not ObjectId.is_valid(variation_id):
        raise HTTPException(status_code=400, detail="Invalid variation id")

    var = await recipe_variations.find_one({"_id": ObjectId(variation_id)})
    if not var:
        raise HTTPException(status_code=404, detail="Variation not found")

    new_status = "approved" if body.action == "approve" else "rejected"
    await recipe_variations.update_one(
        {"_id": ObjectId(variation_id)}, {"$set": {"status": new_status}}
    )

    if body.action == "approve":
        await dishes.update_one({"_id": ObjectId(var["dish_id"])}, {"$inc": {"variation_count": 1}})
        if var.get("author_id") and ObjectId.is_valid(var["author_id"]):
            await users.update_one(
                {"_id": ObjectId(var["author_id"])},
                {"$inc": {"variations_approved_count": 1}},
            )

    return {"id": variation_id, "status": new_status}


# ── Leaderboard ────────────────────────────────────────────────────────────────
@router.get("/api/contributors/top")
async def top_contributors(limit: int = 10):
    cursor = users.find(
        {"$or": [{"dishes_approved_count": {"$gt": 0}}, {"variations_approved_count": {"$gt": 0}}]},
        {"name": 1, "dishes_approved_count": 1, "variations_approved_count": 1},
    )
    docs = await cursor.to_list(100)

    results = []
    for u in docs:
        d = u.get("dishes_approved_count", 0)
        v = u.get("variations_approved_count", 0)
        results.append({
            "id": str(u["_id"]),
            "name": u.get("name", ""),
            "dishes_approved_count": d,
            "variations_approved_count": v,
            "badge": _badge(d, v),
        })

    results.sort(key=lambda x: x["dishes_approved_count"] + x["variations_approved_count"], reverse=True)
    return results[:limit]
