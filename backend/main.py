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


# ── One-time seed endpoint ────────────────────────────────────────────────────
@app.post("/internal/seed-dishes")
async def seed_dishes_endpoint(secret: str):
    if secret != "megeb-seed-2024":
        raise HTTPException(status_code=403, detail="Forbidden")
    from datetime import datetime, timezone

    def dk(name, name_am, cat, region, desc, img, ph=""):
        slug = name.lower().replace(" ","  -").replace("'","").replace("/","-").replace("(","").replace(")","").replace("  -","-").replace(" ","-")
        return {"slug":slug,"name":name,"name_amharic":name_am,"category":cat,"region":region,
                "description":desc,"reference_image_url":img,"phonetic_name":ph,
                "status":"approved","variation_count":0,"search_count":0,"created_at":datetime.now(timezone.utc)}

    def vk(did, vn, ing, steps, tags=None, prep=20, cook=40, sv=4, sp="medium", notes="", story=""):
        return {"dish_id":str(did),"variation_name":vn,"author_id":"system","author_name":"Megeb Kitchen",
                "ingredients":ing,"steps":[{"title":t,"text":x} for t,x in steps],"image_url":"",
                "prep_time_minutes":prep,"cook_time_minutes":cook,"servings":sv,"spice_level":sp,
                "notes":notes,"dietary_tags":tags or [],"story":story,"status":"approved",
                "likes_count":0,"search_count":0,"created_at":datetime.now(timezone.utc)}

    IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg"
    DISH_DATA = [
        dk("Doro Wat","ዶሮ ወጥ","main","All Ethiopia","Ethiopia's national dish — deeply spiced chicken stew with berbere and niter kibbeh, served on injera.","https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doro_wat.jpg/1280px-Doro_wat.jpg","DOH-roh waht"),
        dk("Tibs","ጥብስ","main","All Ethiopia","Tender sautéed beef or lamb with jalapeños, rosemary, onions, and tomatoes.","https://live.staticflickr.com/4092/5002959689_d1a6e6d8e0_b.jpg","tibs"),
        dk("Shiro Wat","ሽሮ ወጥ","main","All Ethiopia","Creamy spiced chickpea flour stew — cornerstone of Ethiopian fasting cuisine.","https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Shiro_be_kibbeh.jpg/1280px-Shiro_be_kibbeh.jpg","SHEE-roh waht"),
        dk("Injera","እንጀራ","main","All Ethiopia","The spongy sourdough teff flatbread — foundation of every Ethiopian meal.","https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Injera_2.jpg/1280px-Injera_2.jpg","in-JEH-rah"),
        dk("Kitfo","ክትፎ","main","Gurage","Ethiopian steak tartare — minced lean beef with mitmita and niter kibbeh.","https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Kitfo.jpg/1280px-Kitfo.jpg","kit-FOH"),
        dk("Firfir","ፍርፍር","main","All Ethiopia","Torn injera soaked in spiced berbere-tomato sauce.",IMG,"fir-FIR"),
        dk("Misir Wat","ምስር ወጥ","main","All Ethiopia","Red lentils slow-cooked in a rich berbere sauce — staple of fasting days.",IMG,"mih-SIR waht"),
        dk("Beyaynetu","በያይነቱ","main","All Ethiopia","The grand Ethiopian vegetarian platter on injera.",IMG,"beh-yay-NEH-too"),
        dk("Gomen","ጎመን","main","All Ethiopia","Ethiopian collard greens sautéed with garlic, onion, and mild spices.",IMG,"GOH-men"),
        dk("Atkilt Wat","አትክልት ወጥ","main","All Ethiopia","Spiced cabbage, carrot, and potato stew — mild and vegan.",IMG,"at-KILT waht"),
        dk("Sambusa","ሳምቡሳ","snack","All Ethiopia","Crispy fried pastry triangles stuffed with spiced lentils or beef.","https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Samosa_with_dipping_sauce.jpg/1280px-Samosa_with_dipping_sauce.jpg","sam-BOO-sah"),
        dk("Chechebsa","ጨጨብሳ","breakfast","Oromia","Shredded flatbread tossed with niter kibbeh and berbere.",IMG,"cheh-cheb-SAH"),
        dk("Genfo","ገንፎ","breakfast","All Ethiopia","Thick teff porridge with niter kibbeh and berbere at the centre.",IMG,"GEN-foh"),
        dk("Kik Alicha","ቂቅ አልጫ","main","All Ethiopia","Yellow split peas with turmeric and garlic — mild and golden.",IMG,"kik ah-LEE-chah"),
        dk("Siga Wat","ስጋ ወጥ","main","All Ethiopia","Beef chunks slow-cooked in fiery berbere stew.",IMG,"SIH-gah waht"),
        dk("Alicha Wat","አልጫ ወጥ","main","All Ethiopia","Mild chicken or lamb stew with turmeric and ginger — no berbere.",IMG,"ah-LEE-chah waht"),
        dk("Fosolia","ፎሶሊያ","main","All Ethiopia","Ethiopian green beans and carrots sautéed with garlic.",IMG,"foh-SOH-lee-ah"),
        dk("Timatim Salad","ቲማቲም ሰላጣ","salad","All Ethiopia","Fresh tomato and jalapeño salad with lemon juice.",IMG,"tee-mah-TEEM"),
        dk("Ful Medames","ፉል","breakfast","All Ethiopia","Mashed fava beans with lemon, garlic, and chilli.","https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Ful_medames.jpg/1280px-Ful_medames.jpg","fool meh-DAH-mes"),
        dk("Buticha","ቡጢቻ","snack","All Ethiopia","Smooth chickpea dip with lemon, garlic, and jalapeño.",IMG,"boo-TEE-chah"),
        dk("Dulet","ዱለት","main","All Ethiopia","Minced tripe, liver, and beef sautéed with mitmita.",IMG,"doo-LET"),
        dk("Niter Kibbeh","ንጥር ቅቤ","condiment","All Ethiopia","Ethiopian spiced clarified butter with onion, garlic, and spices.",IMG,"NIH-ter kib-BEH"),
        dk("Ayib","አይብ","condiment","All Ethiopia","Ethiopian fresh cottage cheese — served alongside spicy stews.",IMG,"AH-yib"),
        dk("Tegabino","ተጋቢኖ","snack","All Ethiopia","Roasted chickpea flour porridge with spiced butter.",IMG,"teh-gah-BEE-noh"),
        dk("Quanta Firfir","ቋንጣ ፍርፍር","main","All Ethiopia","Dried beef rehydrated and mixed with injera in berbere sauce.",IMG,"KWAN-tah fir-FIR"),
    ]

    existing = await dishes.count_documents({})
    if existing > 0:
        await dishes.drop()
        await recipe_variations.drop()

    result = await dishes.insert_many(DISH_DATA)

    id_map = {}
    async for doc in dishes.find({}, {"_id": 1, "name": 1}):
        id_map[doc["name"]] = doc["_id"]

    VAR_DATA = [
        vk(id_map.get("Doro Wat"),"Classic Doro Wat",["1 whole chicken","4 onions","1/3 cup niter kibbeh","3 tbsp berbere","4 hard-boiled eggs","1 tbsp garlic","Salt","Injera"],[("Dry-cook onions","Cook onions no oil 15 min."),("Add butter","Add niter kibbeh, cook 10 min."),("Add spices","Add berbere and garlic, 5 min."),("Add chicken","Cook 30 min."),("Eggs","Add pierced eggs, simmer 20 min."),("Serve","Serve over injera.")],sp="hot",prep=30,cook=90,story="Served at every Ethiopian celebration."),
        vk(id_map.get("Tibs"),"Classic Tibs",["500g beef cubed","2 onions","2 jalapeños","2 tomatoes","2 tbsp niter kibbeh","1 sprig rosemary","Salt"],[("Sear","Heat niter kibbeh, sear meat 4 min."),("Aromatics","Add onions, jalapeños, rosemary."),("Finish","Add tomatoes, cook 5 min.")],sp="medium",prep=15,cook=20),
        vk(id_map.get("Shiro Wat"),"Classic Shiro",["1 cup shiro powder","2 onions","3 cups water","3 tbsp oil","1 tbsp garlic","1 tbsp berbere","Salt"],[("Cook onions","Cook onions 10 min."),("Add spices","Add garlic and berbere."),("Simmer","Add water, whisk shiro, simmer 15 min.")],tags=["vegan","fasting_friendly"],sp="medium",prep=10,cook=25),
        vk(id_map.get("Injera"),"Classic Injera",["3 cups teff flour","3 cups water","1/2 tsp salt"],[("Mix","Combine flour and water."),("Ferment","Leave 2–3 days."),("Cook","Pour on pan, cover 2 min. No flip.")],tags=["vegan","fasting_friendly","gluten_free","dairy_free"],sp="mild",prep=5,cook=30),
        vk(id_map.get("Kitfo"),"Classic Kitfo",["400g lean beef minced","2 tbsp niter kibbeh","1 tsp mitmita","Salt","Ayib to serve"],[("Season","Warm niter kibbeh with mitmita."),("Mix","Toss beef in spiced butter."),("Serve","Serve with ayib and injera.")],tags=["gluten_free"],sp="hot",prep=20,cook=5),
        vk(id_map.get("Firfir"),"Classic Firfir",["2 onions","1/4 cup oil","2 tbsp berbere","2 tomatoes","Salt","2 injera torn"],[("Cook onions","Cook 15 min."),("Add spices","Add berbere, cook 5 min."),("Add injera","Fold in torn injera, coat well.")],tags=["vegan","fasting_friendly"],sp="hot",prep=10,cook=25),
        vk(id_map.get("Misir Wat"),"Classic Misir Wat",["2 cups red lentils","3 onions","3 tbsp berbere","2 tbsp oil","1 tbsp garlic","4 cups water","Salt"],[("Cook onions","Dry-cook 10 min, add oil."),("Add spices","Add berbere and garlic."),("Simmer","Add lentils, simmer 25 min.")],tags=["vegan","fasting_friendly","gluten_free"],sp="hot",prep=10,cook=40),
        vk(id_map.get("Beyaynetu"),"Classic Beyaynetu",["Misir wat","Shiro","Gomen","Atkilt","Fosolia","Injera"],[("Prepare","Cook each separately."),("Arrange","Spoon mounds on injera."),("Serve","Eat communally.")],tags=["vegan","fasting_friendly"],sp="medium",prep=30,cook=60),
        vk(id_map.get("Gomen"),"Classic Gomen",["1 bunch collard greens","2 onions","4 garlic cloves","2 tbsp oil","Salt"],[("Blanch","Boil greens 5 min."),("Sauté","Cook onions and garlic."),("Combine","Add greens, cook 10 min.")],tags=["vegan","fasting_friendly","gluten_free"],sp="mild",prep=15,cook=25),
        vk(id_map.get("Atkilt Wat"),"Classic Atkilt Wat",["1/2 cabbage","3 carrots","3 potatoes","2 onions","1 tsp turmeric","3 tbsp oil","Salt"],[("Cook onions","Cook 8 min."),("Add veg","Add potatoes, carrots, cabbage."),("Finish","Cover, cook 15 min.")],tags=["vegan","fasting_friendly","gluten_free","dairy_free"],sp="mild",prep=15,cook=30),
        vk(id_map.get("Sambusa"),"Lentil Sambusa",["2 cups flour","1 cup lentils","1 onion","2 jalapeños","Oil"],[("Dough","Mix flour and water."),("Fill","Cook lentil filling."),("Fry","Shape and deep-fry.")],tags=["vegan","fasting_friendly"],sp="medium",prep=30,cook=20),
        vk(id_map.get("Chechebsa"),"Classic Chechebsa",["2 kita flatbreads","3 tbsp niter kibbeh","1 tbsp berbere","Honey"],[("Cook kita","Cook flatbread in dry pan."),("Toss","Shred and toss with niter kibbeh."),("Serve","Drizzle honey.")],sp="medium",prep=10,cook=15),
        vk(id_map.get("Genfo"),"Classic Genfo",["1 cup teff flour","3 cups water","2 tbsp niter kibbeh","1 tsp berbere","Salt"],[("Boil","Bring salted water to boil."),("Whisk","Stir in teff, cook 15 min."),("Serve","Make well, fill with niter kibbeh.")],tags=["gluten_free"],sp="medium",prep=5,cook=20),
        vk(id_map.get("Kik Alicha"),"Classic Kik Alicha",["2 cups yellow split peas","2 onions","1 tsp turmeric","3 tbsp oil","3 garlic cloves","Salt"],[("Cook peas","Boil 20 min."),("Sauté","Cook onions, turmeric, garlic."),("Combine","Simmer together 10 min.")],tags=["vegan","fasting_friendly","gluten_free"],sp="mild",prep=10,cook=35),
        vk(id_map.get("Siga Wat"),"Classic Siga Wat",["700g beef","4 onions","3 tbsp berbere","3 tbsp niter kibbeh","1 tbsp garlic","Salt"],[("Cook onions","Dry-cook 15 min, add niter kibbeh."),("Add berbere","Cook 8 min."),("Braise","Add beef, simmer 45 min.")],sp="hot",prep=15,cook=75),
        vk(id_map.get("Alicha Wat"),"Classic Alicha Wat",["1kg chicken or lamb","3 onions","1 tsp turmeric","1 tbsp ginger","4 garlic cloves","3 tbsp niter kibbeh","Salt"],[("Cook onions","Cook 12 min."),("Add spices","Add turmeric, ginger, garlic."),("Add meat","Cook 35 min.")],sp="mild",prep=15,cook=50),
        vk(id_map.get("Fosolia"),"Classic Fosolia",["300g green beans","2 carrots","2 onions","3 garlic cloves","2 tbsp oil","Salt"],[("Sauté","Cook onions and garlic."),("Add veg","Add beans and carrots, cook 12 min.")],tags=["vegan","fasting_friendly","gluten_free"],sp="mild",prep=10,cook=20),
        vk(id_map.get("Timatim Salad"),"Classic Timatim",["4 tomatoes","1 red onion","2 jalapeños","Lemon juice","2 tbsp oil","Salt"],[("Mix","Combine all."),("Rest","Let sit 10 min.")],tags=["vegan","fasting_friendly","gluten_free","dairy_free"],sp="mild",prep=10,cook=0),
        vk(id_map.get("Ful Medames"),"Classic Ful",["2 cups fava beans","Lemon juice","2 garlic cloves","1 jalapeño","2 tbsp oil","Salt"],[("Mash","Mash fava beans."),("Season","Add lemon, garlic, oil."),("Serve","Serve warm.")],tags=["vegan","fasting_friendly","gluten_free"],sp="mild",prep=5,cook=15),
        vk(id_map.get("Buticha"),"Classic Buticha",["2 cups chickpeas","2 tbsp oil","Lemon juice","2 garlic cloves","1 jalapeño","Salt"],[("Blend","Blend all smooth."),("Serve","Drizzle oil, serve cold.")],tags=["vegan","fasting_friendly","gluten_free","dairy_free"],sp="mild",prep=10,cook=0),
        vk(id_map.get("Dulet"),"Classic Dulet",["200g tripe","200g liver","200g beef","2 onions","2 tbsp niter kibbeh","1 tbsp mitmita","Salt"],[("Cook onions","Sauté 8 min."),("Add meats","Add tripe, beef, liver in sequence."),("Season","Add mitmita.")],sp="hot",prep=20,cook=20,sv=3),
        vk(id_map.get("Niter Kibbeh"),"Classic Niter Kibbeh",["500g butter","1 onion","4 garlic cloves","1 tbsp ginger","1/2 tsp turmeric","1 cinnamon stick"],[("Melt","Melt butter slowly."),("Infuse","Simmer aromatics 20 min."),("Strain","Strain into jar.")],tags=["gluten_free"],sp="mild",prep=5,cook=30,sv=16),
        vk(id_map.get("Ayib"),"Classic Ayib",["2 litres whole milk","3 tbsp lemon juice","1/2 tsp salt"],[("Heat","Bring milk near boil."),("Curdle","Add lemon juice."),("Drain","Strain 1 hour.")],tags=["gluten_free"],sp="mild",prep=5,cook=20,sv=6),
        vk(id_map.get("Tegabino"),"Classic Tegabino",["1 cup chickpea flour","2 cups water","2 tbsp niter kibbeh","Salt","Berbere"],[("Toast","Toast flour 3 min."),("Cook","Add water, stir 10 min."),("Serve","Top with niter kibbeh.")],tags=["fasting_friendly"],sp="medium",prep=5,cook=15,sv=2),
        vk(id_map.get("Quanta Firfir"),"Classic Quanta Firfir",["200g dried beef soaked","2 onions","2 tbsp berbere","2 tbsp niter kibbeh","2 injera torn"],[("Cook onions","Sauté in niter kibbeh."),("Add beef","Add quanta and berbere."),("Add injera","Fold in torn injera.")],sp="hot",prep=15,cook=25,sv=3),
    ]

    var_docs = [v for v in VAR_DATA if v.get("dish_id")]
    if var_docs:
        await recipe_variations.insert_many(var_docs)
        for name, did in id_map.items():
            await dishes.update_one({"_id": did}, {"$set": {"variation_count": 1}})

    return {"seeded_dishes": len(result.inserted_ids), "seeded_variations": len(var_docs)}