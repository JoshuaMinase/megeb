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
        slug = name.lower().replace(" ","-").replace("'","").replace("/","-").replace("(","").replace(")","").replace(",","")
        return {"slug":slug,"name":name,"name_amharic":name_am,"category":cat,"region":region,
                "description":desc,"reference_image_url":img,"phonetic_name":ph,
                "status":"approved","variation_count":0,"search_count":0,"created_at":datetime.now(timezone.utc)}

    def vk(did,vn,ing,steps,tags=None,prep=20,cook=40,sv=4,sp="medium",notes="",story=""):
        return {"dish_id":str(did),"variation_name":vn,"author_id":"system","author_name":"Megeb Kitchen",
                "ingredients":ing,"steps":[{"title":t,"text":x} for t,x in steps],"image_url":"",
                "prep_time_minutes":prep,"cook_time_minutes":cook,"servings":sv,"spice_level":sp,
                "notes":notes,"dietary_tags":tags or [],"story":story,"status":"approved",
                "likes_count":0,"search_count":0,"created_at":datetime.now(timezone.utc)}

    IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg"

    DISH_DATA = [
        # ── Wat / Stews ──
        dk("Doro Wat","ዶሮ ወጥ","main","All Ethiopia","Ethiopia's national dish — deeply spiced chicken stew with berbere and niter kibbeh, served on injera.","https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doro_wat.jpg/1280px-Doro_wat.jpg","DOH-roh waht"),
        dk("Siga Wat","ስጋ ወጥ","main","All Ethiopia","Beef chunks slow-cooked in fiery berbere stew with niter kibbeh.","https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doro_wat.jpg/1280px-Doro_wat.jpg","SIH-gah waht"),
        dk("Misir Wat","ምስር ወጥ","main","All Ethiopia","Red lentils slow-cooked in rich berbere sauce — a fasting staple.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Lentil_stew.jpg/1280px-Lentil_stew.jpg","mih-SIR waht"),
        dk("Shiro Wat","ሽሮ ወጥ","main","All Ethiopia","Creamy spiced chickpea flour stew — cornerstone of Ethiopian fasting cuisine.","https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Shiro_be_kibbeh.jpg/1280px-Shiro_be_kibbeh.jpg","SHEE-roh waht"),
        dk("Alicha Wat","አልጫ ወጥ","main","All Ethiopia","Mild chicken or lamb stew with turmeric and ginger — no berbere, gentle on spice.","https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doro_wat.jpg/1280px-Doro_wat.jpg","ah-LEE-chah waht"),
        dk("Kik Alicha","ቂቅ አልጫ","main","All Ethiopia","Yellow split peas with turmeric and garlic — mild, golden, comforting.","https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Yellow_split_pea_soup.jpg/1280px-Yellow_split_pea_soup.jpg","kik ah-LEE-chah"),
        dk("Atkilt Wat","አትክልት ወጥ","main","All Ethiopia","Spiced cabbage, carrot, and potato stew — mild and vegan.","https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Stir_fried_cabbage.jpg/1280px-Stir_fried_cabbage.jpg","at-KILT waht"),
        dk("Bozena Shiro","ቦዘና ሽሮ","main","All Ethiopia","Shiro wat elevated with chunks of beef or lamb stirred in at the end.","https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Shiro_be_kibbeh.jpg/1280px-Shiro_be_kibbeh.jpg","boh-ZEH-nah SHEE-roh"),
        dk("Yesiga Alicha","የስጋ አልጫ","main","All Ethiopia","Mild beef stew cooked with turmeric, ginger, and onions — no spice.","https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doro_wat.jpg/1280px-Doro_wat.jpg","yeh-SIH-gah ah-LEE-chah"),
        dk("Doro Alicha","ዶሮ አልጫ","main","All Ethiopia","Mild chicken stew with turmeric and niter kibbeh — the gentle cousin of Doro Wat.","https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doro_wat.jpg/1280px-Doro_wat.jpg","DOH-roh ah-LEE-chah"),
        # ── Raw / Tartare ──
        dk("Kitfo","ክትፎ","main","Gurage","Ethiopian steak tartare — minced lean beef with mitmita and niter kibbeh.","https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Kitfo.jpg/1280px-Kitfo.jpg","kit-FOH"),
        dk("Gored Gored","ጎረድ ጎረድ","main","Addis Ababa","Cubed raw beef tossed with mitmita, awaze, and niter kibbeh — served rare.","https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Kitfo.jpg/1280px-Kitfo.jpg","GOH-red GOH-red"),
        dk("Dulet","ዱለት","main","All Ethiopia","Minced tripe, liver, and beef sautéed with mitmita and jalapeño.","https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Kitfo.jpg/1280px-Kitfo.jpg","doo-LET"),
        # ── Sautéed / Grilled ──
        dk("Tibs","ጥብስ","main","All Ethiopia","Tender sautéed beef or lamb with jalapeños, rosemary, onions, and tomatoes.","https://live.staticflickr.com/4092/5002959689_d1a6e6d8e0_b.jpg","tibs"),
        dk("Zilzil Tibs","ዝልዝል ጥብስ","main","All Ethiopia","Strips of beef marinated and sautéed with awaze and rosemary.","https://live.staticflickr.com/4092/5002959689_d1a6e6d8e0_b.jpg","ZIL-zil tibs"),
        dk("Derek Tibs","ደረቅ ጥብስ","main","All Ethiopia","Dry-fried crispy beef or lamb tibs — cooked until the edges are crunchy.","https://live.staticflickr.com/4092/5002959689_d1a6e6d8e0_b.jpg","DEH-rek tibs"),
        dk("Gomen Besiga","ጎመን በስጋ","main","All Ethiopia","Collard greens cooked with tender chunks of beef.","https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Gomen.jpg/1280px-Gomen.jpg","GOH-men beh-SIH-gah"),
        dk("Ye'abesha Gomen","የአበሻ ጎመን","main","All Ethiopia","Collard greens braised with onion and spiced butter — a classic side.","https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Gomen.jpg/1280px-Gomen.jpg","yeh-ah-BEH-shah GOH-men"),
        dk("Fosolia","ፎሶሊያ","main","All Ethiopia","Ethiopian green beans and carrots sautéed with garlic.","https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Green_beans.jpg/1280px-Green_beans.jpg","foh-SOH-lee-ah"),
        dk("Gomen","ጎመን","main","All Ethiopia","Ethiopian collard greens sautéed with garlic, onion, and mild spices.","https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Gomen.jpg/1280px-Gomen.jpg","GOH-men"),
    ]


    DISH_DATA += [
        # ── Injera & Firfir ──
        dk("Injera","እንጀራ","main","All Ethiopia","The spongy sourdough teff flatbread — foundation of every Ethiopian meal.","https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Injera_2.jpg/1280px-Injera_2.jpg","in-JEH-rah"),
        dk("Firfir","ፍርፍር","main","All Ethiopia","Torn injera soaked in spiced berbere-tomato sauce — bold and warming.","https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Injera_2.jpg/1280px-Injera_2.jpg","fir-FIR"),
        dk("Quanta Firfir","ቋንጣ ፍርፍር","main","All Ethiopia","Dried beef strips rehydrated and mixed with injera in berbere sauce.","https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Injera_2.jpg/1280px-Injera_2.jpg","KWAN-tah fir-FIR"),
        dk("Enqulal Firfir","እንቁላል ፍርፍር","breakfast","All Ethiopia","Scrambled eggs mixed with torn injera, tomatoes, and jalapeños.","https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Scrambled_eggs.jpg/1280px-Scrambled_eggs.jpg","en-koo-LAL fir-FIR"),
        dk("Kategna","ካተኛ","snack","All Ethiopia","Toasted injera brushed with berbere and niter kibbeh — a beloved snack.","https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Injera_2.jpg/1280px-Injera_2.jpg","kah-TEG-nah"),
        # ── Breakfast ──
        dk("Chechebsa","ጨጨብሳ","breakfast","Oromia","Shredded flatbread tossed with niter kibbeh and berbere.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","cheh-cheb-SAH"),
        dk("Genfo","ገንፎ","breakfast","All Ethiopia","Thick teff porridge with niter kibbeh and berbere at the centre.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","GEN-foh"),
        dk("Ful Medames","ፉል","breakfast","All Ethiopia","Mashed fava beans with lemon, garlic, and chilli.","https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Ful_medames.jpg/1280px-Ful_medames.jpg","fool meh-DAH-mes"),
        dk("Enqulal Tibs","እንቁላል ጥብስ","breakfast","All Ethiopia","Ethiopian scrambled eggs sautéed with tomatoes, jalapeños, and onions.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","en-koo-LAL tibs"),
        dk("Kinche","ቅንጨ","breakfast","All Ethiopia","Cracked wheat porridge served with niter kibbeh — a warming breakfast.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","KIN-cheh"),
        dk("Teff Porridge","ጤፍ ገንፎ","breakfast","All Ethiopia","Simple teff grain porridge cooked with milk or water and a touch of honey.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","teff GEN-foh"),
        # ── Vegetarian / Fasting ──
        dk("Beyaynetu","በያይነቱ","main","All Ethiopia","The grand Ethiopian vegetarian platter — colourful fasting dishes on injera.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","beh-yay-NEH-too"),
        dk("Timatim Salad","ቲማቲም ሰላጣ","salad","All Ethiopia","Fresh tomato and jalapeño salad dressed with lemon juice and olive oil.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","tee-mah-TEEM"),
        dk("Buticha","ቡጢቻ","snack","All Ethiopia","Smooth chickpea dip with lemon, garlic, and jalapeño — served cold.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","boo-TEE-chah"),
        dk("Tegabino","ተጋቢኖ","snack","All Ethiopia","Roasted chickpea flour porridge cooked with spiced butter.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","teh-gah-BEE-noh"),
        dk("Fassolia","ፋሶሊያ","main","All Ethiopia","White kidney beans slow-cooked with tomatoes, onions, and spices.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","fah-SOH-lee-ah"),
        dk("Yetsom Beyaynetu","የጾም በያይነቱ","main","All Ethiopia","A strict fasting platter with no animal products — the full vegan spread.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","yeh-TSOM beh-yay-NEH-too"),
        dk("Dinich Alicha","ዲኒች አልጫ","main","All Ethiopia","Potato stew with turmeric and mild spices — simple and comforting.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","DIH-nich ah-LEE-chah"),
        dk("Tikel Gomen","ጥቅል ጎመን","main","All Ethiopia","Shredded cabbage sautéed with carrots, turmeric, and garlic.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","TIH-kel GOH-men"),
        dk("Yemisir Kik","የምስር ቂቅ","main","All Ethiopia","Split red lentils cooked mild with turmeric — a lighter fasting dish.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","yeh-MIH-sir kik"),
    ]


    DISH_DATA += [
        # ── Snacks & Street Food ──
        dk("Sambusa","ሳምቡሳ","snack","All Ethiopia","Crispy fried pastry triangles stuffed with spiced lentils or beef.","https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Samosa_with_dipping_sauce.jpg/1280px-Samosa_with_dipping_sauce.jpg","sam-BOO-sah"),
        dk("Andeguday","አንደጓይ","snack","Tigray","Spiced minced beef or lentils wrapped in a fried dough pocket.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","an-deh-GWAI"),
        dk("Dabo Kolo","ዳቦ ቆሎ","snack","All Ethiopia","Tiny crunchy baked or fried dough bites spiced with berbere.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","DAH-boh KOH-loh"),
        dk("Kolo","ቆሎ","snack","All Ethiopia","Roasted barley, chickpeas, and sunflower seeds — the Ethiopian trail mix.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","KOH-loh"),
        dk("Fetira","ፈጢራ","snack","All Ethiopia","Thin fried flatbread drizzled with honey or filled with eggs.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","feh-TEE-rah"),
        # ── Condiments & Sauces ──
        dk("Niter Kibbeh","ንጥር ቅቤ","condiment","All Ethiopia","Ethiopian spiced clarified butter with onion, garlic, ginger, and warming spices.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","NIH-ter kib-BEH"),
        dk("Ayib","አይብ","condiment","All Ethiopia","Ethiopian fresh cottage cheese — mild and crumbly, served with spicy stews.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","AH-yib"),
        dk("Berbere","በርበሬ","condiment","All Ethiopia","The bold Ethiopian spice blend — chilli, fenugreek, coriander, and more.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","ber-BEH-reh"),
        dk("Mitmita","ምጥሚጣ","condiment","All Ethiopia","A fiery Ethiopian spice blend with bird's eye chilli and cardamom.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","mit-MEE-tah"),
        dk("Awaze","አዋዜ","condiment","All Ethiopia","Spicy Ethiopian chilli paste made with berbere, tej, and niter kibbeh.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","ah-WAH-zeh"),
        # ── Soups ──
        dk("Shorba","ሾርባ","main","All Ethiopia","Ethiopian lamb or beef soup with vegetables, spices, and noodles.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","SHOR-bah"),
        dk("Yetsom Shorba","የጾም ሾርባ","main","All Ethiopia","Fasting vegetable soup with lentils, tomatoes, and mild spices.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","yeh-TSOM SHOR-bah"),
        # ── Breads ──
        dk("Ambasha","አምባሻ","snack","Tigray / Amhara","Decorative round flatbread stamped with patterns — baked for celebrations.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","am-BAH-shah"),
        dk("Dabo","ዳቦ","snack","All Ethiopia","Ethiopian honey bread — slightly sweet, soft, and fluffy.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","DAH-boh"),
        dk("Kita","ቂጣ","breakfast","All Ethiopia","Thin unleavened flatbread pan-cooked and served with niter kibbeh.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","KEE-tah"),
        # ── Drinks ──
        dk("Tej","ጠጅ","main","All Ethiopia","Traditional Ethiopian honey wine — amber, slightly fizzy, mildly sweet.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","tehj"),
        dk("Tella","ጠላ","main","All Ethiopia","Traditional Ethiopian home-brewed sorghum beer — earthy and lightly sour.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","TEL-lah"),
        dk("Buna","ቡና","main","All Ethiopia","The Ethiopian coffee ceremony — freshly roasted and brewed with popcorn.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","BOO-nah"),
        dk("Shameta","ሻሜታ","main","Amhara","Soured milk drink mixed with barley flour — refreshing and tangy.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","shah-MEH-tah"),
        dk("Atmet","አጥሜት","breakfast","All Ethiopia","A warm drink made of roasted barley flour, niter kibbeh, and honey.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","at-MET"),
    ]


    DISH_DATA += [
        # ── Regional Specialties ──
        dk("Tigrayan Zigni","ትግራይ ዝግኒ","main","Tigray","Tigrayan slow-cooked lamb or beef in a deeply spiced berbere sauce.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","zig-NEE"),
        dk("Tihlo","ጥሕሎ","main","Tigray","Barley flour dumplings served with a spiced lamb or beef broth.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","TIH-loh"),
        dk("Shahan Ful","ሻሃን ፉል","breakfast","Harar","Harar-style fava beans cooked with clarified butter and served in clay bowls.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","shah-HAN fool"),
        dk("Ye'dorho Wot be Doro","የዶርሆ ወጥ","main","Wolaita","Wolaita-style chicken stew with kocho flatbread instead of injera.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","yeh-DOR-hoh wot"),
        dk("Kocho","ቆጮ","main","Southern Ethiopia","Fermented false banana flatbread from Southern Ethiopia — dense and earthy.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","KOH-choh"),
        dk("Bulla","ቡላ","breakfast","Southern Ethiopia","Starchy porridge made from the false banana plant — smooth and mild.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","BOO-lah"),
        dk("Enjera Firfir be Doro","እንጀራ ፍርፍር በዶሮ","main","All Ethiopia","Firfir enriched with shredded chicken — a heartier version of the classic.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","en-JEH-rah fir-FIR"),
        # ── Desserts & Sweets ──
        dk("Ye'asel Dabo","የዓሥለ ዳቦ","snack","All Ethiopia","Ethiopian sweet honey cake served at holidays and celebrations.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","yeh-AH-sel DAH-boh"),
        dk("Himbasha","ሂምባሻ","snack","Eritrea / Tigray","Celebration bread flavoured with cardamom and black seed — soft and fragrant.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","him-BAH-shah"),
        # ── Organ Meat & Offal ──
        dk("Tire Siga","ጥሬ ስጋ","main","All Ethiopia","Fresh raw beef served immediately after slaughter — the Ethiopian sashimi.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","TIH-reh SIH-gah"),
        dk("Feseg","ፌሰግ","main","Amhara","Special lamb dish prepared for Easter — slow-cooked with spiced butter.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","FEH-seg"),
        dk("Kurt","ቁርጥ","main","All Ethiopia","Fresh-cut raw or lightly cooked beef chunks seasoned at the table.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","koort"),
        # ── Egg Dishes ──
        dk("Enqulal be Timatim","እንቁላል በቲማቲም","breakfast","All Ethiopia","Eggs poached in a spiced tomato sauce with jalapeños and onions.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","en-koo-LAL beh tee-mah-TEEM"),
        # ── More Legumes ──
        dk("Yebeg Alicha","የበግ አልጫ","main","All Ethiopia","Mild lamb stew with turmeric, ginger, and potato — tender and fragrant.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","yeh-BEG ah-LEE-chah"),
        dk("Yebeg Wat","የበግ ወጥ","main","All Ethiopia","Spiced lamb stew cooked in berbere and niter kibbeh.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","yeh-BEG waht"),
        dk("Kikil","ቂቅል","main","All Ethiopia","Boiled lamb or goat leg served with broth and awaze dipping sauce.","https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ethiopian_cuisine.jpg/1280px-Ethiopian_cuisine.jpg","kee-KIL"),
    ]

    existing = await dishes.count_documents({})
    if existing > 0:
        await dishes.drop()
        await recipe_variations.drop()

    result = await dishes.insert_many(DISH_DATA)

    id_map = {}
    async for doc in dishes.find({}, {"_id":1,"name":1}):
        id_map[doc["name"]] = doc["_id"]

    # One variation per dish with key dishes getting full recipes
    VAR_DATA = []
    full = {
        "Doro Wat": vk(id_map.get("Doro Wat"),"Classic Doro Wat",["1 whole chicken","4 onions","1/3 cup niter kibbeh","3 tbsp berbere","4 hard-boiled eggs","1 tbsp garlic","Salt","Injera"],[("Dry-cook onions","Cook onions no oil 15 min."),("Add butter","Add niter kibbeh, cook 10 min."),("Berbere","Add berbere and garlic, 5 min."),("Chicken","Add chicken, cook 30 min."),("Eggs","Add pierced eggs, simmer 20 min."),("Serve","Serve over injera.")],sp="hot",prep=30,cook=90,story="Served at every Ethiopian celebration."),
        "Tibs": vk(id_map.get("Tibs"),"Classic Tibs",["500g beef cubed","2 onions","2 jalapeños","2 tomatoes","2 tbsp niter kibbeh","1 rosemary sprig","Salt"],[("Sear","Heat niter kibbeh, sear meat 4 min."),("Aromatics","Add onions, jalapeños, rosemary."),("Finish","Add tomatoes, cook 5 min.")],sp="medium",prep=15,cook=20),
        "Shiro Wat": vk(id_map.get("Shiro Wat"),"Classic Shiro",["1 cup shiro powder","2 onions","3 cups water","3 tbsp oil","1 tbsp garlic","1 tbsp berbere","Salt"],[("Cook onions","Cook onions 10 min."),("Spices","Add garlic and berbere."),("Simmer","Add water, whisk shiro, simmer 15 min.")],tags=["vegan","fasting_friendly"],sp="medium",prep=10,cook=25),
        "Injera": vk(id_map.get("Injera"),"Classic Teff Injera",["3 cups teff flour","3 cups water","1/2 tsp salt"],[("Mix","Combine flour and water."),("Ferment","Leave 2–3 days."),("Cook","Pour on pan, cover 2 min. No flip.")],tags=["vegan","fasting_friendly","gluten_free","dairy_free"],sp="mild",prep=5,cook=30),
        "Kitfo": vk(id_map.get("Kitfo"),"Classic Kitfo",["400g lean beef minced","2 tbsp niter kibbeh","1 tsp mitmita","Salt","Ayib to serve"],[("Season","Warm niter kibbeh with mitmita."),("Mix","Toss beef in spiced butter."),("Serve","Serve with ayib and injera.")],tags=["gluten_free"],sp="hot",prep=20,cook=5,story="A Gurage delicacy served at weddings."),
        "Misir Wat": vk(id_map.get("Misir Wat"),"Classic Misir Wat",["2 cups red lentils","3 onions","3 tbsp berbere","2 tbsp oil","1 tbsp garlic","4 cups water","Salt"],[("Cook onions","Dry-cook 10 min, add oil."),("Spices","Add berbere and garlic."),("Simmer","Add lentils, simmer 25 min.")],tags=["vegan","fasting_friendly","gluten_free"],sp="hot",prep=10,cook=40),
        "Beyaynetu": vk(id_map.get("Beyaynetu"),"Classic Beyaynetu",["Misir wat","Shiro","Gomen","Atkilt","Fosolia","Injera"],[("Prepare","Cook each dish separately."),("Arrange","Spoon mounds on large injera."),("Serve","Eat communally.")],tags=["vegan","fasting_friendly"],sp="medium",prep=30,cook=60),
        "Gomen": vk(id_map.get("Gomen"),"Classic Gomen",["1 bunch collard greens","2 onions","4 garlic cloves","2 tbsp oil","Salt"],[("Blanch","Boil greens 5 min."),("Sauté","Cook onions and garlic."),("Combine","Add greens, cook 10 min.")],tags=["vegan","fasting_friendly","gluten_free"],sp="mild",prep=15,cook=25),
        "Atkilt Wat": vk(id_map.get("Atkilt Wat"),"Classic Atkilt Wat",["1/2 cabbage","3 carrots","3 potatoes","2 onions","1 tsp turmeric","3 tbsp oil","Salt"],[("Cook onions","Cook 8 min."),("Add veg","Add potatoes, carrots, cabbage."),("Finish","Cover, cook 15 min.")],tags=["vegan","fasting_friendly","gluten_free","dairy_free"],sp="mild",prep=15,cook=30),
        "Sambusa": vk(id_map.get("Sambusa"),"Lentil Sambusa",["2 cups flour","1 cup lentils","1 onion","2 jalapeños","Oil for frying"],[("Dough","Mix flour and water, rest 20 min."),("Fill","Cook lentil filling."),("Fry","Shape and deep-fry.")],tags=["vegan","fasting_friendly"],sp="medium",prep=30,cook=20),
        "Chechebsa": vk(id_map.get("Chechebsa"),"Classic Chechebsa",["2 kita flatbreads","3 tbsp niter kibbeh","1 tbsp berbere","Honey"],[("Cook kita","Cook flatbread in dry pan."),("Toss","Shred and toss with niter kibbeh."),("Serve","Drizzle honey.")],sp="medium",prep=10,cook=15),
        "Genfo": vk(id_map.get("Genfo"),"Classic Genfo",["1 cup teff flour","3 cups water","2 tbsp niter kibbeh","1 tsp berbere","Salt"],[("Boil","Bring salted water to boil."),("Whisk","Stir in teff, cook 15 min."),("Serve","Make well, fill with niter kibbeh.")],tags=["gluten_free"],sp="medium",prep=5,cook=20),
        "Ful Medames": vk(id_map.get("Ful Medames"),"Classic Ful",["2 cups fava beans","Lemon juice","2 garlic cloves","1 jalapeño","2 tbsp oil","Salt"],[("Mash","Mash fava beans."),("Season","Add lemon, garlic, oil."),("Serve","Serve warm.")],tags=["vegan","fasting_friendly","gluten_free"],sp="mild",prep=5,cook=15),
        "Kik Alicha": vk(id_map.get("Kik Alicha"),"Classic Kik Alicha",["2 cups yellow split peas","2 onions","1 tsp turmeric","3 tbsp oil","3 garlic cloves","Salt"],[("Cook peas","Boil 20 min."),("Sauté","Cook onions, turmeric, garlic."),("Combine","Simmer together 10 min.")],tags=["vegan","fasting_friendly","gluten_free"],sp="mild",prep=10,cook=35),
        "Siga Wat": vk(id_map.get("Siga Wat"),"Classic Siga Wat",["700g beef","4 onions","3 tbsp berbere","3 tbsp niter kibbeh","1 tbsp garlic","Salt"],[("Cook onions","Dry-cook 15 min, add niter kibbeh."),("Berbere","Cook 8 min."),("Braise","Add beef, simmer 45 min.")],sp="hot",prep=15,cook=75),
        "Firfir": vk(id_map.get("Firfir"),"Classic Firfir",["2 onions","1/4 cup oil","2 tbsp berbere","2 tomatoes","Salt","2 injera torn"],[("Cook onions","Cook 15 min."),("Spices","Add berbere, cook 5 min."),("Add injera","Fold in torn injera.")],tags=["vegan","fasting_friendly"],sp="hot",prep=10,cook=25),
        "Niter Kibbeh": vk(id_map.get("Niter Kibbeh"),"Classic Niter Kibbeh",["500g butter","1 onion","4 garlic cloves","1 tbsp ginger","1/2 tsp turmeric","1 cinnamon stick"],[("Melt","Melt butter slowly."),("Infuse","Simmer aromatics 20 min."),("Strain","Strain into jar.")],tags=["gluten_free"],sp="mild",prep=5,cook=30,sv=16),
        "Ayib": vk(id_map.get("Ayib"),"Classic Ayib",["2 litres whole milk","3 tbsp lemon juice","Salt"],[("Heat","Bring milk near boil."),("Curdle","Add lemon juice."),("Drain","Strain 1 hour.")],tags=["gluten_free"],sp="mild",prep=5,cook=20,sv=6),
        "Buna": vk(id_map.get("Buna"),"Ethiopian Coffee Ceremony",["Green coffee beans","Water","Incense","Popcorn to serve"],[("Roast","Roast green beans over charcoal, shaking constantly."),("Grind","Grind roasted beans in mortar."),("Brew","Boil in jebena clay pot 10 min."),("Serve","Pour into small cups. Repeat 3 rounds.")],tags=["vegan","fasting_friendly","gluten_free","dairy_free"],sp="mild",prep=15,cook=20,sv=6,story="The Ethiopian coffee ceremony is a sacred ritual of hospitality taking 1–2 hours."),
        "Tej": vk(id_map.get("Tej"),"Classic Tej",["1 kg honey","5 litres water","Gesho hops"],[("Mix","Dissolve honey in warm water."),("Add gesho","Add gesho twigs for bitterness."),("Ferment","Ferment 1–2 weeks until bubbly."),("Strain","Strain and serve in berele glass.")],tags=["gluten_free","dairy_free"],sp="mild",prep=10,cook=0,sv=10),
    }
    for name, var in full.items():
        if var and var.get("dish_id"):
            VAR_DATA.append(var)

    # Simple variation for every remaining dish
    for d in DISH_DATA:
        name = d["name"]
        if name not in full and id_map.get(name):
            VAR_DATA.append(vk(id_map[name], f"Classic {name}",
                [f"See traditional recipe for {name}"],
                [("Prepare","Gather ingredients as per tradition."),
                 ("Cook","Follow traditional method."),
                 ("Serve","Serve with injera.")],
                sp="medium",prep=20,cook=40))

    var_docs = [v for v in VAR_DATA if v.get("dish_id")]
    if var_docs:
        await recipe_variations.insert_many(var_docs)
        for name, did in id_map.items():
            await dishes.update_one({"_id":did},{"$set":{"variation_count":1}})

    return {"seeded_dishes": len(result.inserted_ids), "seeded_variations": len(var_docs)}

