from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    nationality: str = "Ethiopian"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RecipeStep(BaseModel):
    title: str
    text: str


class RecipeCreate(BaseModel):
    name: str
    description: str
    ingredients: List[str]
    steps: List[RecipeStep]
    nationality: Optional[str] = "Ethiopian"
    image: Optional[str] = ""
    youtube_url: Optional[str] = ""
    prep_time: Optional[str] = ""
    cook_time: Optional[str] = ""
    servings: Optional[str] = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict


# ── Pantry ────────────────────────────────────────────────────────────────────
class PantryItemCreate(BaseModel):
    name: str
    quantity: Optional[str] = ""
    unit: Optional[str] = ""
    expiry: Optional[str] = ""


# ── Nutrition Log ─────────────────────────────────────────────────────────────
class NutritionLogCreate(BaseModel):
    recipe_id: Optional[str] = ""
    recipe_name: str
    calories: Optional[float] = 0
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fat: Optional[float] = 0
    date: Optional[str] = ""


# ── AI Generate ───────────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    ingredients: Optional[List[str]] = []
    cuisine: Optional[str] = ""
    diet: Optional[str] = ""
    time_limit: Optional[str] = ""
    servings: Optional[str] = ""
    prompt: Optional[str] = ""


# ── AI Substitute ─────────────────────────────────────────────────────────────
class SubstituteRequest(BaseModel):
    ingredient: str
    dish_context: Optional[str] = ""


# ── Dishes ────────────────────────────────────────────────────────────────────
DIETARY_TAGS = {"fasting_friendly", "vegan", "gluten_free", "dairy_free", "nut_free"}


class DishCreate(BaseModel):
    name: str
    name_amharic: Optional[str] = ""
    category: str
    region: Optional[str] = ""
    description: str
    reference_image_url: Optional[str] = ""
    phonetic_name: Optional[str] = ""


class VariationCreate(BaseModel):
    variation_name: str
    ingredients: List[str]
    steps: List[Dict]           # [{"title": ..., "text": ...}]
    image_url: Optional[str] = ""
    youtube_url: Optional[str] = ""
    prep_time_minutes: Optional[int] = 0
    cook_time_minutes: Optional[int] = 0
    servings: Optional[int] = 2
    spice_level: Optional[str] = "medium"  # mild | medium | spicy
    notes: Optional[str] = ""
    dietary_tags: Optional[List[str]] = []
    story: Optional[str] = ""


# ── Moderation ────────────────────────────────────────────────────────────────
class ModerationAction(BaseModel):
    action: str  # "approve" | "reject"


# ── Collections ───────────────────────────────────────────────────────────────
class CollectionCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    cover_image_url: Optional[str] = ""
    dish_ids: Optional[List[str]] = []
    is_active: Optional[bool] = True


class CollectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    dish_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None
