from fastapi import APIRouter, Depends, HTTPException
from models.schemas import PantryItemCreate
from database import db
from auth import get_current_user
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/pantry", tags=["pantry"])
pantry = db["pantry"]


def _out(doc: dict) -> dict:
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    return out


@router.get("/")
async def list_pantry(user=Depends(get_current_user)):
    items = await pantry.find({"user_id": str(user["_id"])}).to_list(200)
    return [_out(i) for i in items]


@router.post("/", status_code=201)
async def add_item(body: PantryItemCreate, user=Depends(get_current_user)):
    doc = body.model_dump()
    doc["user_id"] = str(user["_id"])
    doc["added_at"] = datetime.now(timezone.utc)
    result = await pantry.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _out(doc)


@router.delete("/{item_id}")
async def remove_item(item_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item id")
    oid = ObjectId(item_id)
    result = await pantry.delete_one({"_id": oid, "user_id": str(user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(404, "Item not found")
    return {"deleted": True}
