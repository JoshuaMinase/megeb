from fastapi import APIRouter, Depends, HTTPException, Query
from models.schemas import NutritionLogCreate
from database import db
from auth import get_current_user
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/nutrition", tags=["nutrition"])
nutrition = db["nutrition_logs"]


def _out(doc: dict) -> dict:
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    return out


@router.get("")
async def list_logs(date: str = Query(None), user=Depends(get_current_user)):
    query = {"user_id": str(user["_id"])}
    if date:
        query["date"] = date
    items = await nutrition.find(query).sort("logged_at", -1).to_list(100)
    return [_out(i) for i in items]


@router.post("", status_code=201)
async def log_meal(body: NutritionLogCreate, user=Depends(get_current_user)):
    doc = body.model_dump()
    doc["user_id"] = str(user["_id"])
    doc["logged_at"] = datetime.now(timezone.utc)
    if not doc.get("date"):
        doc["date"] = datetime.now(timezone.utc).date().isoformat()
    result = await nutrition.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _out(doc)


@router.delete("/{log_id}")
async def delete_log(log_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(log_id):
        raise HTTPException(status_code=400, detail="Invalid log id")
    oid = ObjectId(log_id)
    result = await nutrition.delete_one({"_id": oid, "user_id": str(user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(404, "Log not found")
    return {"deleted": True}
