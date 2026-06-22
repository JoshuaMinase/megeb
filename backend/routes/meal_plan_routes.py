from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from database import db
from auth import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/meal-plan", tags=["meal-plan"])
meal_plans = db["meal_plans"]


class MealPlanSave(BaseModel):
    week_label: str
    days: Dict[str, Optional[str]] = {}


@router.get("/{week_label}")
async def get_meal_plan(week_label: str, user=Depends(get_current_user)):
    doc = await meal_plans.find_one({
        "user_id": str(user["_id"]),
        "week_label": week_label,
    })
    if not doc:
        return {"week_label": week_label, "days": {}}
    return {
        "week_label": doc["week_label"],
        "days": doc.get("days", {}),
    }


@router.post("/", status_code=201)
async def save_meal_plan(body: MealPlanSave, user=Depends(get_current_user)):
    if not body.week_label.strip():
        raise HTTPException(status_code=400, detail="week_label is required")

    doc = {
        "user_id": str(user["_id"]),
        "week_label": body.week_label.strip(),
        "days": body.days,
        "updated_at": datetime.now(timezone.utc),
    }
    await meal_plans.update_one(
        {"user_id": doc["user_id"], "week_label": doc["week_label"]},
        {"$set": doc},
        upsert=True,
    )
    return {"week_label": doc["week_label"], "days": doc["days"]}
