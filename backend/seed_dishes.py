"""Run once: python seed_dishes.py — populates MongoDB dishes + variations."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "megeb")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


def dish(name, name_am, category, region, desc, img, phonetic=""):
    slug = name.lower().replace(" ", "-").replace("'", "").replace("/", "-").replace("(", "").replace(")", "")
    return {
        "slug": slug,
        "name": name,
        "name_amharic": name_am,
        "category": category,
        "region": region,
        "description": desc,
        "reference_image_url": img,
        "phonetic_name": phonetic,
        "status": "approved",
        "variation_count": 0,
        "search_count": 0,
        "created_at": datetime.now(timezone.utc),
    }


def variation(dish_id, var_name, ingredients, steps, tags=None, prep=20, cook=40, servings=4, spice="medium", notes="", story=""):
    return {
        "dish_id": str(dish_id),
        "variation_name": var_name,
        "author_id": "system",
        "author_name": "Megeb Kitchen",
        "ingredients": ingredients,
        "steps": [{"title": t, "text": x} for t, x in steps],
        "image_url": "",
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "servings": servings,
        "spice_level": spice,
        "notes": notes,
        "dietary_tags": tags or [],
        "story": story,
        "status": "approved",
        "likes_count": 0,
        "search_count": 0,
        "created_at": datetime.now(timezone.utc),
    }


# ── Dishes ────────────────────────────────────────────────────────────────────

DISHES = [
    dish("Doro Wat", "ዶሮ ወጥ", "main", "All Ethiopia",
         "Ethiopia's national dish — deeply spiced chicken stew simmered with berbere and niter kibbeh, served on injera.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doro_wat.jpg/1280px-Doro_wat.jpg",
         "DOH-roh waht"),

    dish("Tibs", "ጥብስ", "main", "All Ethiopia",
         "Tender sautéed beef or lamb with jalapeños, rosemary, onions, and tomatoes — one of Ethiopia's most-loved dishes.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Tibs.jpg/1280px-Tibs.jpg",
         "tibs"),

    dish("Shiro Wat", "ሽሮ ወጥ", "main", "All Ethiopia",
         "Creamy spiced chickpea flour stew — the cornerstone of Ethiopian fasting cuisine.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Shiro_be_kibbeh.jpg/1280px-Shiro_be_kibbeh.jpg",
         "SHEE-roh waht"),

    dish("Injera", "እንጀራ", "main", "All Ethiopia",
         "The spongy sourdough teff flatbread that is the foundation of every Ethiopian meal.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Injera_2.jpg/1280px-Injera_2.jpg",
         "in-JEH-rah"),

    dish("Kitfo", "ክትፎ", "main", "Gurage",
         "Ethiopian steak tartare — minced lean beef seasoned with mitmita and niter kibbeh. A Gurage delicacy.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Kitfo.jpg/1280px-Kitfo.jpg",
         "kit-FOH"),

    dish("Firfir", "ፍርፍር", "main", "All Ethiopia",
         "Torn injera soaked in spiced berbere-tomato sauce. Bold, warming, and quick to prepare.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Firfir.jpg/1280px-Firfir.jpg",
         "fir-FIR"),

    dish("Misir Wat", "ምስር ወጥ", "main", "All Ethiopia",
         "Red lentils slow-cooked in a rich berbere sauce — a staple of Ethiopian fasting days.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Misir_wat.jpg/1280px-Misir_wat.jpg",
         "mih-SIR waht"),

    dish("Beyaynetu", "በያይነቱ", "main", "All Ethiopia",
         "The grand Ethiopian vegetarian platter — a colourful spread of fasting dishes served on injera.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Ethiopian_Injera_with_various_wots.jpg/1280px-Ethiopian_Injera_with_various_wots.jpg",
         "beh-yay-NEH-too"),

    dish("Gomen", "ጎመን", "main", "All Ethiopia",
         "Ethiopian collard greens sautéed with garlic, onion, and mild spices. A classic fasting side.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Gomen.jpg/1280px-Gomen.jpg",
         "GOH-men"),

    dish("Atkilt Wat", "አትክልት ወጥ", "main", "All Ethiopia",
         "Spiced cabbage, carrot, and potato stew — mild, comforting, and fully vegan.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Atkilt_wat.jpg/1280px-Atkilt_wat.jpg",
         "at-KILT waht"),
]


DISHES += [
    dish("Sambusa", "ሳምቡሳ", "snack", "All Ethiopia",
         "Crispy fried pastry triangles stuffed with spiced lentils or beef. A popular Ethiopian street food.",
         "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&q=80",
         "sam-BOO-sah"),

    dish("Chechebsa", "ጨጨብሳ", "breakfast", "Oromia",
         "Shredded flatbread tossed with niter kibbeh and berbere — a beloved Ethiopian breakfast.",
         "https://images.unsplash.com/photo-1585518419759-7186f017a4b0?w=800&q=80",
         "cheh-cheb-SAH"),

    dish("Genfo", "ገንፎ", "breakfast", "All Ethiopia",
         "Thick teff porridge served with a well of niter kibbeh and berbere at the centre.",
         "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
         "GEN-foh"),

    dish("Kik Alicha", "ቂቅ አልጫ", "main", "All Ethiopia",
         "Yellow split peas cooked with turmeric and garlic — mild, golden, and comforting.",
         "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80",
         "kik ah-LEE-chah"),

    dish("Siga Wat", "ስጋ ወጥ", "main", "All Ethiopia",
         "Beef chunks slow-cooked in a fiery berbere stew with niter kibbeh.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Siga_wat.jpg/1280px-Siga_wat.jpg",
         "SIH-gah waht"),

    dish("Alicha Wat", "አልጫ ወጥ", "main", "All Ethiopia",
         "Mild chicken or lamb stew with turmeric, ginger, and garlic — no berbere, gentle on spice.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Alicha_wat.jpg/1280px-Alicha_wat.jpg",
         "ah-LEE-chah waht"),

    dish("Fosolia", "ፎሶሊያ", "main", "All Ethiopia",
         "Ethiopian green beans and carrots sautéed with garlic and ginger.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Green_beans_and_carrots.jpg/1280px-Green_beans_and_carrots.jpg",
         "foh-SOH-lee-ah"),

    dish("Timatim Salad", "ቲማቲም ሰላጣ", "salad", "All Ethiopia",
         "Fresh Ethiopian tomato and jalapeño salad dressed with lemon juice and olive oil.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Tomato_salad.jpg/1280px-Tomato_salad.jpg",
         "tee-mah-TEEM"),

    dish("Ful Medames", "ፉል", "breakfast", "All Ethiopia",
         "Mashed fava beans with lemon, garlic, and chilli — a popular Ethiopian breakfast.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Ful_medames.jpg/1280px-Ful_medames.jpg",
         "fool meh-DAH-mes"),

    dish("Buticha", "ቡጢቻ", "snack", "All Ethiopia",
         "Smooth chickpea dip seasoned with lemon, garlic, and jalapeño — served cold with injera.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Chickpea_dip.jpg/1280px-Chickpea_dip.jpg",
         "boo-TEE-chah"),
]

DISHES += [
    dish("Dulet", "ዱለት", "main", "All Ethiopia",
         "Minced tripe, liver, and beef sautéed with mitmita and jalapeño — a bold Ethiopian offal dish.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Ethiopian_meat_dish.jpg/1280px-Ethiopian_meat_dish.jpg",
         "doo-LET"),

    dish("Quanta Firfir", "ቋንጣ ፍርፍር", "main", "All Ethiopia",
         "Dried beef strips rehydrated and mixed with injera in a spiced berbere sauce.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Beef_tibs.jpg/1280px-Beef_tibs.jpg",
         "KWAN-tah fir-FIR"),

    dish("Niter Kibbeh", "ንጥር ቅቤ", "condiment", "All Ethiopia",
         "Ethiopian spiced clarified butter infused with onion, garlic, ginger, and warming spices.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Niter_kibbeh.jpg/1280px-Niter_kibbeh.jpg",
         "NIH-ter kib-BEH"),

    dish("Ayib", "አይብ", "condiment", "All Ethiopia",
         "Ethiopian fresh cottage cheese — mild and crumbly, served alongside spicy stews.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Ayib.jpg/1280px-Ayib.jpg",
         "AH-yib"),

    dish("Tegabino", "ተጋቢኖ", "snack", "All Ethiopia",
         "Roasted chickpea flour porridge cooked with spiced butter — a popular Ethiopian street food.",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Chickpea_flour.jpg/1280px-Chickpea_flour.jpg",
         "teh-gah-BEE-noh"),
]



# ── Variations (one per dish) ─────────────────────────────────────────────────

VARIATIONS = {
    "Doro Wat": lambda did: variation(did, "Classic Doro Wat",
        ["1 whole chicken, cut into pieces", "4 large onions, finely chopped",
         "1/3 cup niter kibbeh", "3 tbsp berbere", "4 hard-boiled eggs",
         "1 tbsp garlic paste", "Salt", "Injera to serve"],
        [("Dry-cook onions", "Cook onions with no oil 15 min, stirring constantly."),
         ("Add niter kibbeh", "Add spiced butter, cook 10 min until golden."),
         ("Add berbere", "Add berbere and garlic, cook 5 min."),
         ("Add chicken", "Add chicken pieces, coat well, cook 30 min."),
         ("Add eggs", "Add pierced hard-boiled eggs, simmer 20 min until thick."),
         ("Serve", "Serve hot over fresh injera.")],
        spice="hot", prep=30, cook=90,
        story="Served at almost every Ethiopian celebration. The dry-cooked onions are the secret to its deep flavour."),

    "Tibs": lambda did: variation(did, "Classic Tibs",
        ["500g beef or lamb, cubed", "2 onions, sliced", "2 jalapeños",
         "2 tomatoes", "2 tbsp niter kibbeh", "1 sprig rosemary", "Salt and pepper"],
        [("Heat pan", "Heat pan over high heat, add niter kibbeh."),
         ("Sear meat", "Sear meat without stirring for 3–4 min."),
         ("Add aromatics", "Add onions, jalapeños, rosemary. Toss 5 min."),
         ("Finish", "Add tomatoes, cook 5 min. Season and serve.")],
        spice="medium", prep=15, cook=20),

    "Shiro Wat": lambda did: variation(did, "Classic Shiro Wat",
        ["1 cup shiro powder", "2 onions, finely chopped", "3 cups water",
         "3 tbsp oil", "1 tbsp garlic paste", "1 tbsp berbere", "Salt"],
        [("Cook onions", "Heat oil, cook onions 10 min until golden."),
         ("Add spices", "Add garlic and berbere, cook 2 min."),
         ("Add water", "Pour in water, bring to gentle boil."),
         ("Whisk shiro", "Slowly whisk in shiro powder to avoid lumps."),
         ("Simmer", "Simmer 10–15 min stirring until thick. Season.")],
        tags=["vegan", "fasting_friendly"], spice="medium", prep=10, cook=25),

    "Injera": lambda did: variation(did, "Classic Teff Injera",
        ["3 cups teff flour", "3 cups water", "1/2 tsp salt"],
        [("Mix batter", "Combine teff flour and water. Stir well."),
         ("Ferment", "Cover and leave at room temperature 2–3 days until bubbly."),
         ("Cook", "Pour thin layer onto hot pan. Cover 2 min. Do not flip."),
         ("Cool", "Slide onto rack. Cool before stacking.")],
        tags=["vegan", "fasting_friendly", "dairy_free", "gluten_free"],
        spice="mild", prep=5, cook=30,
        notes="True teff injera is naturally gluten-free. Longer ferment = more sour flavour."),

    "Kitfo": lambda did: variation(did, "Classic Kitfo",
        ["400g very lean beef, minced", "2 tbsp niter kibbeh", "1 tsp mitmita",
         "1/2 tsp cardamom", "Salt", "Ayib to serve", "Injera to serve"],
        [("Season butter", "Warm niter kibbeh gently, stir in mitmita and cardamom."),
         ("Mix beef", "Toss minced beef with spiced butter until fully coated."),
         ("Serve", "Serve immediately with ayib and injera.")],
        tags=["gluten_free"], spice="hot", prep=20, cook=5,
        story="A Gurage delicacy served at weddings. Fresh beef and quality niter kibbeh make all the difference."),

    "Firfir": lambda did: variation(did, "Classic Firfir",
        ["2 large onions", "1/4 cup oil", "2 tbsp berbere", "1 tbsp garlic paste",
         "2 tomatoes, diced", "1 cup water", "Salt", "2 pieces injera, torn"],
        [("Cook onions", "Heat oil, cook onions 10–15 min until golden."),
         ("Add spices", "Add garlic and berbere, cook 5 min."),
         ("Simmer sauce", "Add tomatoes and water, simmer 10 min."),
         ("Mix injera", "Fold in torn injera, coat each piece. Serve warm.")],
        tags=["vegan", "fasting_friendly"], spice="hot", prep=10, cook=25),

    "Misir Wat": lambda did: variation(did, "Classic Misir Wat",
        ["2 cups red lentils", "3 onions, finely chopped", "3 tbsp berbere",
         "2 tbsp oil", "1 tbsp garlic paste", "1 tsp ginger", "4 cups water", "Salt"],
        [("Cook onions", "Dry-cook onions 10 min, add oil, cook 5 more min."),
         ("Add spices", "Add berbere, garlic, ginger. Cook 5 min."),
         ("Add lentils", "Add rinsed lentils and water. Bring to boil."),
         ("Simmer", "Simmer 25 min stirring until thick and creamy.")],
        tags=["vegan", "fasting_friendly", "gluten_free"], spice="hot", prep=10, cook=40),

    "Beyaynetu": lambda did: variation(did, "Classic Beyaynetu",
        ["Misir wat", "Shiro wat", "Gomen", "Atkilt wat", "Timatim salad", "Fosolia", "Injera"],
        [("Prepare each dish", "Cook misir, shiro, gomen, atkilt, and fosolia separately."),
         ("Arrange", "Line a large injera on a tray. Spoon each dish in separate mounds."),
         ("Serve", "Tear injera pieces and scoop stews. Eat communally.")],
        tags=["vegan", "fasting_friendly"], spice="medium", prep=30, cook=60),

    "Gomen": lambda did: variation(did, "Classic Gomen",
        ["1 large bunch collard greens, chopped", "2 onions, sliced", "4 garlic cloves",
         "1 tbsp ginger", "3 tbsp oil", "1 jalapeño", "Salt"],
        [("Blanch greens", "Boil collards 5 min, drain and squeeze dry."),
         ("Sauté aromatics", "Heat oil, cook onions 8 min. Add garlic and ginger."),
         ("Combine", "Add greens and jalapeño, toss, cook 10 min. Season.")],
        tags=["vegan", "fasting_friendly", "gluten_free"], spice="mild", prep=15, cook=25),

    "Atkilt Wat": lambda did: variation(did, "Classic Atkilt Wat",
        ["1/2 head cabbage, chopped", "3 carrots, sliced", "3 potatoes, cubed",
         "2 onions", "1 tsp turmeric", "1 tsp cumin", "3 tbsp oil", "Salt"],
        [("Cook onions", "Heat oil, cook onions 8 min."),
         ("Add spices", "Add turmeric and cumin, cook 2 min."),
         ("Add veg", "Add potatoes and carrots 10 min. Add cabbage."),
         ("Finish", "Cover and cook 15 min until tender.")],
        tags=["vegan", "fasting_friendly", "gluten_free", "dairy_free"], spice="mild", prep=15, cook=30),

    "Sambusa": lambda did: variation(did, "Lentil Sambusa",
        ["2 cups flour", "Water and salt for dough", "1 cup cooked lentils",
         "1 onion, diced", "2 jalapeños", "1 tsp cumin", "Oil for frying"],
        [("Make dough", "Mix flour, salt, water to firm dough. Rest 20 min."),
         ("Make filling", "Cook onion, jalapeño, cumin with lentils. Cool."),
         ("Shape", "Roll dough thin, fold into cones, fill, seal."),
         ("Fry", "Deep-fry in hot oil until golden, 3–4 min.")],
        tags=["vegan", "fasting_friendly"], spice="medium", prep=30, cook=20),

    "Chechebsa": lambda did: variation(did, "Classic Chechebsa",
        ["2 kita flatbreads", "3 tbsp niter kibbeh", "1 tbsp berbere", "Honey to serve"],
        [("Make kita", "Cook thin flatbreads in dry pan, 2 min per side."),
         ("Shred", "Tear into bite-size pieces."),
         ("Toss", "Toss warm pieces with niter kibbeh and berbere."),
         ("Serve", "Drizzle with honey. Serve for breakfast.")],
        spice="medium", prep=10, cook=15),

    "Genfo": lambda did: variation(did, "Classic Genfo",
        ["1 cup teff flour", "3 cups water", "1/2 tsp salt", "2 tbsp niter kibbeh", "1 tsp berbere"],
        [("Boil water", "Bring salted water to boil."),
         ("Whisk teff", "Slowly whisk in teff flour. Stir constantly 15 min until very thick."),
         ("Serve", "Mound in bowl, make a well, fill with niter kibbeh and berbere.")],
        tags=["gluten_free"], spice="medium", prep=5, cook=20),

    "Kik Alicha": lambda did: variation(did, "Classic Kik Alicha",
        ["2 cups yellow split peas", "3 cups water", "2 onions",
         "1 tsp turmeric", "3 tbsp oil", "3 garlic cloves", "Salt"],
        [("Cook peas", "Boil split peas in water 20 min until soft."),
         ("Sauté", "Cook onions in oil 8 min, add turmeric and garlic."),
         ("Combine", "Add peas to onion mix, simmer 10 min. Mash slightly.")],
        tags=["vegan", "fasting_friendly", "gluten_free"], spice="mild", prep=10, cook=35),

    "Siga Wat": lambda did: variation(did, "Classic Siga Wat",
        ["700g beef, cubed", "4 onions", "3 tbsp berbere", "3 tbsp niter kibbeh",
         "1 tbsp garlic", "1 tsp ginger", "Salt"],
        [("Cook onions", "Dry-cook onions 15 min, add niter kibbeh, cook 10 min."),
         ("Add berbere", "Add berbere, garlic, ginger. Cook 8 min."),
         ("Braise", "Add beef, add 1/2 cup water. Simmer 45 min until tender.")],
        spice="hot", prep=15, cook=75),

    "Alicha Wat": lambda did: variation(did, "Classic Alicha Wat",
        ["1kg chicken or lamb pieces", "3 onions", "1 tsp turmeric",
         "1 tbsp ginger", "4 garlic cloves", "3 tbsp niter kibbeh", "Salt"],
        [("Cook onions", "Cook onions in niter kibbeh 12 min."),
         ("Add spices", "Add turmeric, ginger, garlic. Cook 3 min."),
         ("Add meat", "Add meat, cook 35 min until tender.")],
        spice="mild", prep=15, cook=50),

    "Fosolia": lambda did: variation(did, "Classic Fosolia",
        ["300g green beans", "2 carrots, julienned", "2 onions",
         "3 garlic cloves", "2 tbsp oil", "Salt"],
        [("Sauté", "Heat oil, cook onions 5 min, add garlic."),
         ("Add veg", "Add beans and carrots, cook 12 min until tender. Season.")],
        tags=["vegan", "fasting_friendly", "gluten_free"], spice="mild", prep=10, cook=20),

    "Timatim Salad": lambda did: variation(did, "Classic Timatim Salad",
        ["4 tomatoes, diced", "1 red onion, diced", "2 jalapeños, sliced",
         "Juice of 1 lemon", "2 tbsp olive oil", "Salt"],
        [("Mix", "Combine all ingredients."),
         ("Rest", "Let sit 10 min before serving.")],
        tags=["vegan", "fasting_friendly", "gluten_free", "dairy_free"], spice="mild", prep=10, cook=0),

    "Ful Medames": lambda did: variation(did, "Classic Ful Medames",
        ["2 cups cooked fava beans", "Juice of 1 lemon", "2 garlic cloves, minced",
         "1 jalapeño", "2 tbsp olive oil", "Salt"],
        [("Mash", "Roughly mash fava beans with a fork."),
         ("Season", "Add lemon, garlic, jalapeño, oil, salt. Mix well."),
         ("Serve", "Serve warm with injera or bread.")],
        tags=["vegan", "fasting_friendly", "gluten_free"], spice="mild", prep=5, cook=15),

    "Buticha": lambda did: variation(did, "Classic Buticha",
        ["2 cups cooked chickpeas", "2 tbsp olive oil", "Juice of 1 lemon",
         "2 garlic cloves", "1 jalapeño", "Salt"],
        [("Blend", "Blend all ingredients until smooth."),
         ("Serve", "Drizzle with oil, serve chilled with injera.")],
        tags=["vegan", "fasting_friendly", "gluten_free"], spice="mild", prep=10, cook=0),

    "Niter Kibbeh": lambda did: variation(did, "Classic Niter Kibbeh",
        ["500g unsalted butter", "1 onion, chopped", "4 garlic cloves",
         "1 tbsp ginger", "1/2 tsp turmeric", "1/4 tsp cardamom", "1 cinnamon stick"],
        [("Melt butter", "Melt butter over low heat."),
         ("Add aromatics", "Add all aromatics, simmer 20 min — do not boil."),
         ("Strain", "Pour through fine sieve into jar. Keeps 3 months refrigerated.")],
        tags=["gluten_free"], spice="mild", prep=5, cook=30, servings=16),

    "Ayib": lambda did: variation(did, "Classic Ayib",
        ["2 litres whole milk", "3 tbsp lemon juice", "1/2 tsp salt"],
        [("Heat milk", "Bring milk to near boil."),
         ("Curdle", "Add lemon juice, stir gently. Curds will form."),
         ("Drain", "Pour through cheesecloth, drain 1 hour. Salt and serve.")],
        tags=["gluten_free"], spice="mild", prep=5, cook=20, servings=6),

    "Dulet": lambda did: variation(did, "Classic Dulet",
        ["200g tripe, minced", "200g liver, minced", "200g lean beef, minced",
         "2 onions", "2 tbsp niter kibbeh", "1 tbsp mitmita", "1 jalapeño", "Salt"],
        [("Cook onions", "Sauté onions in niter kibbeh 8 min."),
         ("Add meats", "Add tripe first (5 min), then beef (3 min), then liver (2 min)."),
         ("Season", "Add mitmita, jalapeño, salt. Toss and serve with injera.")],
        spice="hot", prep=20, cook=20, servings=3),

    "Quanta Firfir": lambda did: variation(did, "Classic Quanta Firfir",
        ["200g quanta (dried beef), soaked", "2 onions", "2 tbsp berbere",
         "2 tbsp niter kibbeh", "1 tbsp garlic", "Salt", "2 pieces injera, torn"],
        [("Cook onions", "Sauté onions in niter kibbeh 10 min."),
         ("Add beef", "Add quanta and berbere, cook 10 min."),
         ("Add injera", "Fold in torn injera, coat well. Serve hot.")],
        spice="hot", prep=15, cook=25, servings=3),

    "Tegabino": lambda did: variation(did, "Classic Tegabino",
        ["1 cup roasted chickpea flour", "2 cups water", "2 tbsp niter kibbeh", "Salt", "Berbere to taste"],
        [("Toast flour", "Dry-toast chickpea flour in pan 3 min until fragrant."),
         ("Add water", "Add water gradually, whisk to avoid lumps."),
         ("Cook", "Stir over medium heat 10 min until thick. Add niter kibbeh.")],
        tags=["fasting_friendly"], spice="medium", prep=5, cook=15, servings=2),
}



# ── Main ──────────────────────────────────────────────────────────────────────

async def seed():
    dishes_col = db["dishes"]
    variations_col = db["recipe_variations"]

    existing = await dishes_col.count_documents({})
    if existing > 0:
        print(f"Found {existing} existing dishes — dropping and reseeding.")
        await dishes_col.drop()
        await variations_col.drop()

    result = await dishes_col.insert_many(DISHES)
    print(f"Seeded {len(result.inserted_ids)} dishes.")

    # Build name → _id map
    id_map = {}
    async for doc in dishes_col.find({}, {"_id": 1, "name": 1}):
        id_map[doc["name"]] = doc["_id"]

    # Insert one variation per dish
    var_docs = []
    for dish_name, var_fn in VARIATIONS.items():
        if dish_name in id_map:
            var_docs.append(var_fn(id_map[dish_name]))

    if var_docs:
        vr = await variations_col.insert_many(var_docs)
        print(f"Seeded {len(vr.inserted_ids)} variations.")

        # Set variation_count = 1 on each dish that has a variation
        for dish_name in VARIATIONS:
            if dish_name in id_map:
                await dishes_col.update_one(
                    {"_id": id_map[dish_name]},
                    {"$set": {"variation_count": 1}}
                )

    print("Done! Your Megeb database is ready.")


asyncio.run(seed())
