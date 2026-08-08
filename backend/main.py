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

load_dotenv()

# â”€â”€ Startup env validation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_REQUIRED = ["GROQ_API_KEY", "JWT_SECRET", "MONGO_URL"]
_missing = [k for k in _REQUIRED if not os.environ.get(k)]
if _missing:
    print(f"WARNING: Missing env vars: {', '.join(_missing)}. Some features may not work.")

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
    if secret != "megeb-seed-2024":
        raise HTTPException(status_code=403, detail="Forbidden")

    # Reliable image URLs from Wikimedia Commons (direct file links that allow hotlinking)
    IMAGES = {
        "Doro Wat":         "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Siga Wat":         "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Misir Wat":        "https://upload.wikimedia.org/wikipedia/commons/4/4a/Ful_medames.jpg",
        "Shiro Wat":        "https://upload.wikimedia.org/wikipedia/commons/5/5e/Shiro_be_kibbeh.jpg",
        "Alicha Wat":       "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Kik Alicha":       "https://upload.wikimedia.org/wikipedia/commons/4/4a/Ful_medames.jpg",
        "Atkilt Wat":       "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800",
        "Bozena Shiro":     "https://upload.wikimedia.org/wikipedia/commons/5/5e/Shiro_be_kibbeh.jpg",
        "Yesiga Alicha":    "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Doro Alicha":      "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Kitfo":            "https://upload.wikimedia.org/wikipedia/commons/c/c9/Kitfo.jpg",
        "Gored Gored":      "https://upload.wikimedia.org/wikipedia/commons/c/c9/Kitfo.jpg",
        "Dulet":            "https://upload.wikimedia.org/wikipedia/commons/c/c9/Kitfo.jpg",
        "Tire Siga":        "https://upload.wikimedia.org/wikipedia/commons/c/c9/Kitfo.jpg",
        "Kurt":             "https://upload.wikimedia.org/wikipedia/commons/c/c9/Kitfo.jpg",
        "Tibs":             "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
        "Zilzil Tibs":      "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
        "Derek Tibs":       "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
        "Gomen Besiga":     "https://images.unsplash.com/photo-1576021182211-9ea8dce94d28?w=800",
        "Ye'abesha Gomen":  "https://images.unsplash.com/photo-1576021182211-9ea8dce94d28?w=800",
        "Fosolia":          "https://images.unsplash.com/photo-1551248429-40975aa4de74?w=800",
        "Gomen":            "https://images.unsplash.com/photo-1576021182211-9ea8dce94d28?w=800",
        "Injera":           "https://upload.wikimedia.org/wikipedia/commons/9/9e/Injera_2.jpg",
        "Firfir":           "https://upload.wikimedia.org/wikipedia/commons/9/9e/Injera_2.jpg",
        "Quanta Firfir":    "https://upload.wikimedia.org/wikipedia/commons/9/9e/Injera_2.jpg",
        "Enqulal Firfir":   "https://images.unsplash.com/photo-1525184782196-8e2e4a1b7de3?w=800",
        "Kategna":          "https://upload.wikimedia.org/wikipedia/commons/9/9e/Injera_2.jpg",
        "Chechebsa":        "https://upload.wikimedia.org/wikipedia/commons/9/9e/Injera_2.jpg",
        "Genfo":            "https://images.unsplash.com/photo-1551248429-40975aa4de74?w=800",
        "Ful Medames":      "https://upload.wikimedia.org/wikipedia/commons/4/4a/Ful_medames.jpg",
        "Enqulal Tibs":     "https://images.unsplash.com/photo-1525184782196-8e2e4a1b7de3?w=800",
        "Kinche":           "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
        "Teff Porridge":    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
        "Beyaynetu":        "https://upload.wikimedia.org/wikipedia/commons/d/d5/Ethiopian_cuisine.jpg",
        "Yetsom Beyaynetu": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Ethiopian_cuisine.jpg",
        "Timatim Salad":    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800",
        "Buticha":          "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
        "Tegabino":         "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
        "Fassolia":         "https://images.unsplash.com/photo-1551248429-40975aa4de74?w=800",
        "Dinich Alicha":    "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=800",
        "Tikel Gomen":      "https://images.unsplash.com/photo-1576021182211-9ea8dce94d28?w=800",
        "Yemisir Kik":      "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
        "Sambusa":          "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800",
        "Andeguday":        "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800",
        "Dabo Kolo":        "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=800",
        "Kolo":             "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=800",
        "Fetira":           "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
        "Niter Kibbeh":     "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800",
        "Ayib":             "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800",
        "Berbere":          "https://images.unsplash.com/photo-1532336414038-cf19250c5757?w=800",
        "Mitmita":          "https://images.unsplash.com/photo-1532336414038-cf19250c5757?w=800",
        "Awaze":            "https://images.unsplash.com/photo-1532336414038-cf19250c5757?w=800",
        "Shorba":           "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
        "Yetsom Shorba":    "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
        "Ambasha":          "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
        "Dabo":             "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
        "Kita":             "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
        "Himbasha":         "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
        "Tej":              "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        "Tella":            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        "Buna":             "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800",
        "Shameta":          "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        "Atmet":            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800",
        "Tigrayan Zigni":   "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Tihlo":            "https://upload.wikimedia.org/wikipedia/commons/d/d5/Ethiopian_cuisine.jpg",
        "Shahan Ful":       "https://upload.wikimedia.org/wikipedia/commons/4/4a/Ful_medames.jpg",
        "Kocho":            "https://upload.wikimedia.org/wikipedia/commons/d/d5/Ethiopian_cuisine.jpg",
        "Bulla":            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
        "Enqulal be Timatim": "https://images.unsplash.com/photo-1525184782196-8e2e4a1b7de3?w=800",
        "Yebeg Alicha":     "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Yebeg Wat":        "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Kikil":            "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
        "Feseg":            "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Ye'abesha Gomen":  "https://images.unsplash.com/photo-1576021182211-9ea8dce94d28?w=800",
        "Enjera Firfir be Doro": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Injera_2.jpg",
        "Ye'dorho Wot be Doro": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Doro_wat.jpg",
        "Ye'asel Dabo":     "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
        "Gomen Besiga":     "https://images.unsplash.com/photo-1576021182211-9ea8dce94d28?w=800",
    }

    updated = 0
    async for dish in dishes.find({}):
        name = dish.get("name", "")
        if name in IMAGES:
            await dishes.update_one(
                {"_id": dish["_id"]},
                {"$set": {"reference_image_url": IMAGES[name]}}
            )
            updated += 1

    return {"updated": updated, "total_in_map": len(IMAGES)}
