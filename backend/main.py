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

# ── Startup env validation ─────────────────────────────────────────────────────
_REQUIRED = ["GROQ_API_KEY", "JWT_SECRET", "MONGO_URL"]
_missing = [k for k in _REQUIRED if not os.environ.get(k)]
if _missing:
    raise RuntimeError(f"Missing required env vars: {', '.join(_missing)}")

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
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(","),
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

# Frontend is served by nginx in production, but can be mounted locally for development
# On Render, we don't mount the frontend as it's a separate service
if os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))):
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")