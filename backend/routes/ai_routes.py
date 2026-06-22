import json
import re
import bleach
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import httpx
import os
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.schemas import GenerateRequest, SubstituteRequest

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])
limiter = Limiter(key_func=get_remote_address)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
MODEL        = "llama-3.1-8b-instant"   # free, fast


def _headers():
    return {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = "food"


class ImageRequest(BaseModel):
    image_base64: str


SYSTEM_FOOD = """You are Megeb's Ethiopian cooking assistant.
The user will give you a list of ingredients they have at home.
Your ONLY job is to suggest Ethiopian dishes they can make with those ingredients.
List 2–4 matching Ethiopian recipes. For each one give: the dish name, a one-line description, and the key ingredients from their list that it uses.
If none of their ingredients match any Ethiopian dish, politely say so and suggest what common Ethiopian ingredients to add.
Never suggest non-Ethiopian food."""

SYSTEM_GENERATE = """You are an expert chef AI. Generate a complete recipe based on what the user provides.
Respond with ONLY valid JSON — no markdown, no extra text:
{"name":"...","description":"...","nationality":"...","ingredients":["..."],"steps":[{"title":"...","text":"..."}],"prep_time":"...","cook_time":"...","servings":"...","nutrition":{"calories":0,"protein":"0g","carbs":"0g","fat":"0g"},"tags":["..."]}"""


async def call_groq(messages: list) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(503, "Groq API key not set. Add GROQ_API_KEY to backend/.env")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(GROQ_URL, headers=_headers(), json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
        })

    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]

    try:
        err = resp.json().get("error", {}).get("message", resp.text)
    except Exception:
        err = resp.text

    if resp.status_code == 401:
        raise HTTPException(401, "Invalid Groq API key.")
    if resp.status_code == 429:
        raise HTTPException(429, "Rate limit hit — try again in a moment.")
    raise HTTPException(502, f"AI error: {err}")


def _extract_json(content: str):
    content = re.sub(r"```(?:json)?\s*", "", content).strip().rstrip("`")
    try:
        return json.loads(content)
    except Exception:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


@router.post("/chat")
@limiter.limit("20/minute")
async def ai_chat(request: Request, body: ChatRequest):
    content = await call_groq([
        {"role": "system", "content": SYSTEM_FOOD},
        {"role": "user",   "content": body.message},
    ])
    return {"reply": content}


@router.post("/image-recipe")
@limiter.limit("10/minute")
async def image_to_recipe(request: Request, body: ImageRequest):
    content = await call_groq([
        {"role": "system", "content": "You are a recipe expert. The user uploaded a food photo but vision is unavailable. Ask them to describe the dish and you'll generate the recipe."},
        {"role": "user",   "content": "I uploaded a food photo. Please help me identify and get the recipe."},
    ])
    return {"recipe": None, "raw": content}


@router.post("/generate")
@limiter.limit("10/minute")
async def generate_recipe(request: Request, body: GenerateRequest):
    parts = []
    if body.ingredients:
        parts.append(f"Available ingredients: {', '.join(body.ingredients)}")
    if body.cuisine:
        parts.append(f"Cuisine: {body.cuisine}")
    if body.diet:
        parts.append(f"Diet: {body.diet}")
    if body.time_limit:
        parts.append(f"Time limit: {body.time_limit}")
    if body.servings:
        parts.append(f"Servings: {body.servings}")
    if body.prompt:
        parts.append(body.prompt)

    user_msg = "\n".join(parts) if parts else "Suggest a delicious recipe."
    content  = await call_groq([
        {"role": "system", "content": SYSTEM_GENERATE},
        {"role": "user",   "content": user_msg},
    ])
    recipe = _extract_json(content)
    return {"recipe": recipe} if recipe else {"recipe": None, "raw": content}



@router.post("/substitute")
@limiter.limit("15/minute")
async def substitute_ingredient(request: Request, body: SubstituteRequest):
    ingredient = bleach.clean(body.ingredient, tags=[], strip=True)[:100] if body.ingredient else ""
    context    = bleach.clean(body.dish_context or "", tags=[], strip=True)[:200]
    if not ingredient:
        raise HTTPException(status_code=400, detail="ingredient is required")

    prompt = f"I'm making {context + ' and ' if context else ''}an Ethiopian dish. I can't find \"{ingredient}\" where I live. Suggest 2–3 practical substitutes available in most Western supermarkets. For each substitute give: the name, why it works, and any adjustment needed (quantity, technique). Keep it brief."
    content = await call_groq([
        {"role": "system", "content": "You are a practical Ethiopian cooking assistant helping people outside Ethiopia find ingredient substitutes."},
        {"role": "user",   "content": prompt},
    ])
    return {"substitutes": content}
