"""
Seed script sourced from the Gursha cookbook by Beejhy Barhany.
Populates MongoDB with authentic Ethiopian dishes and recipe variations.
Run: python seed_gursha.py
"""
import asyncio, os, re
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "megeb")]
dishes_col = db["dishes"]
vars_col   = db["recipe_variations"]

NOW = datetime.now(timezone.utc)


def slugify(name):
    s = name.lower()
    s = re.sub(r"['\u2019/()&]", "", s)
    s = re.sub(r"[\s]+", "-", s.strip())
    return s


def d(name, name_am, category, region, desc, img="", phonetic=""):
    return {
        "slug": slugify(name),
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
        "created_at": NOW,
    }


def v(dish_id, vname, ing, steps, tags=None, prep=15, cook=30, sv=4, sp="medium", notes="", story=""):
    return {
        "dish_id": str(dish_id),
        "variation_name": vname,
        "author_id": "system",
        "author_name": "Gursha Cookbook",
        "ingredients": ing,
        "steps": [{"title": t, "text": x} for t, x in steps],
        "image_url": "",
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "servings": sv,
        "spice_level": sp,
        "notes": notes,
        "dietary_tags": tags or [],
        "story": story,
        "status": "approved",
        "likes_count": 0,
        "search_count": 0,
        "created_at": NOW,
    }



# ── DISH DEFINITIONS ─────────────────────────────────────────────────────────
# Each entry: (dish_doc, variation_factory)
# variation_factory receives the inserted dish _id and returns a variation doc.

SEED_DATA = []

# ════════════════════════════════════════════════════════════════════════════
# CHAPTER 1 — MAKEDA'S KITCHEN (Spice Blends, Bases & Condiments)
# ════════════════════════════════════════════════════════════════════════════

SEED_DATA.append((
    d("Berbere", "በርበሬ", "condiment", "All Ethiopia",
      "Ethiopia's most iconic spice blend — a rich, aromatic mix of dried chilies, korarima, and warming spices that forms the backbone of countless stews.",
      "", "BER-beh-reh"),
    lambda did: v(did, "Gursha Berbere",
        ["1 cup paprika", "½ cup cayenne pepper",
         "3 tbsp ground roasted korarima (or ground cardamom)",
         "2 tbsp ground ginger", "1 tbsp onion powder",
         "1 tbsp ground coriander", "1 tbsp ground cumin",
         "1 tbsp black pepper", "2 tbsp fine sea salt",
         "1½ tsp ground cloves", "1½ tsp ground cinnamon",
         "1½ tsp ground nutmeg", "1½ tsp ground fenugreek"],
        [("Mix the spices",
          "In a small bowl, mix all the ingredients together until thoroughly combined. Transfer to an airtight jar."),
         ("Store",
          "Store at room temperature for up to 6 months. This recipe makes about 2½ cups — enough for a full batch of kulet/silsi stew base with some left over.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=0, sv=40, sp="spicy",
        story="This flavorful, aromatic seasoning blend says a lot about the cook who mixes it. Author Beejhy Barhany starts with plenty of dried chili pepper and adds a healthy dose of korarima for nutty, herbal notes. Feel free to use this as a starting point, adding more of any flavors you want to emphasize.")
))

SEED_DATA.append((
    d("Kulet / Silsi", "ቁለት", "condiment", "All Ethiopia",
      "The fragrant, crimson-colored base for all thick Ethiopian stews — slow-cooked onions, garlic, ginger, and berbere that melt together into one deeply flavored sauce.",
      "", "KOO-let"),
    lambda did: v(did, "Gursha Kulet",
        ["10–12 large yellow onions, peeled and quartered",
         "6 cups vegetable oil, plus more if needed",
         "2 cups berbere spice blend",
         "4 tsp minced garlic", "2 tsp minced fresh ginger",
         "3 tbsp fine sea salt", "8 cups hot water",
         "6 oz tomato paste",
         "1 tbsp ground roasted korarima (or ground cardamom)"],
        [("Purée the onions",
          "In a food processor, purée the onions until smooth."),
         ("Evaporate the onion water",
          "Pour onions into a large pot and bring to a simmer over high heat. Cook, stirring occasionally, until most water has evaporated, 35–40 minutes."),
         ("Add oil and berbere",
          "Stir in the oil and simmer 5 minutes. Stir in the berbere, garlic, ginger, and salt. The mixture should be moist — add more hot water, ½ cup at a time, if it looks dry. Cover and cook over medium heat until onions turn red, 10–15 minutes."),
         ("Finish the base",
          "Add the hot water and tomato paste. Stir well, bring to a simmer, then cook uncovered about 1 hour until fragrant. Remove from heat, stir in korarima, and cool."),
         ("Store",
          "Store in an airtight container in the refrigerator for up to 2 weeks, or freeze for up to 3 months.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=20, cook=90, sv=32, sp="spicy",
        notes="Makes about 16 cups. Use as the base for doro wot, messer wot, beg wot, and assa wot.",
        story="The foundation of all thick, spicy Ethiopian stews. Let this crimson-colored base bubble for a few hours, and you can have dinner all week.")
))

SEED_DATA.append((
    d("Niter Kibbeh / Tesmi", "ንጥር ቅቤ", "condiment", "All Ethiopia",
      "Spice-infused Ethiopian clarified butter — simmered with korarima, besobela, and aromatics until deep mahogany and fragrant. The secret flavour behind countless Ethiopian dishes.",
      "", "NIT-er KIB-beh"),
    lambda did: v(did, "Gursha Niter Kibbeh",
        ["2 lb (8 sticks) unsalted butter",
         "½ yellow onion, chopped",
         "4 tsp minced garlic", "2 tsp minced fresh ginger",
         "1 tbsp dried besobela (Ethiopian basil) or dried regular basil",
         "1 tbsp ground roasted korarima (or ground cardamom)",
         "1 tbsp ground turmeric",
         "1 tsp ground fenugreek or fenugreek seeds",
         "1 tsp green cardamom pods",
         "4 whole cloves",
         "3 sprigs fresh thyme, or ½ tsp dried thyme"],
        [("Melt and infuse",
          "In a medium saucepan, melt the butter over medium-low heat. Add the onion, garlic, ginger, besobela, korarima, turmeric, fenugreek, cardamom pods, cloves, and thyme. Simmer until the butter foams, about 15 minutes."),
         ("Brown the butter",
          "Stir the foam down and continue simmering until the butter becomes brown, clear, and fragrant, 5–10 more minutes."),
         ("Strain and store",
          "Cool to room temperature. Strain through a fine-mesh strainer or cheesecloth, pressing the solids to extract all flavour. Discard solids. Store in a jar in the refrigerator for up to 6 months or in the freezer for up to 1 year.")],
        tags=["gluten_free", "vegetarian"], prep=5, cook=25, sv=24, sp="mild",
        notes="Makes about 3 cups. Use to sauté meat, swap for oil in stew recipes, drizzle over vegetables, or stir into porridge.",
        story="Add spices to butter, simmer until the butter turns a deep mahogany, and you have a staple of Ethiopian cooking that will last in the refrigerator for months.")
))

SEED_DATA.append((
    d("Ayib / Ajibo", "አይብ", "condiment", "All Ethiopia",
      "Fresh Ethiopian cheese — mild, crumbly curds made from whole milk and vinegar, used as a cooling garnish against spicy stews much like Indian raita or Greek tzatziki.",
      "", "AH-yib"),
    lambda did: v(did, "Gursha Ayib",
        ["2 quarts whole milk",
         "1 cup distilled white vinegar",
         "Optional: niter kibbeh and berbere for serving"],
        [("Heat the milk",
          "In a medium pot, warm the milk over low heat, stirring occasionally. Bring to a gentle simmer."),
         ("Add vinegar",
          "Slowly swirl in the vinegar, stirring constantly, until fully incorporated. Leave over low heat as curds form in the centre of the pot."),
         ("Strain the curds",
          "Set a fine-mesh strainer over a large bowl and line with cheesecloth. When the milk has formed a solid white mass (about 10 minutes), immediately strain. Do not press. Keep over the bowl 5–10 minutes until it stops dripping. Crumble into small curds with a fork."),
         ("Serve",
          "Serve garnished with niter kibbeh and a sprinkle of berbere, if desired. Store in the refrigerator for up to 1 week.")],
        tags=["gluten_free", "vegetarian"], prep=5, cook=15, sv=8, sp="mild",
        story="Why make fresh cheese yourself? Because it's easier than you might expect, and its pure milky flavour provides a soothing, cooling counterbalance to spicy stews.")
))

SEED_DATA.append((
    d("Delleh", "ደለህ", "condiment", "All Ethiopia",
      "Ethiopian berbere paste — deep red, concentrated, and ready to melt seamlessly into stews. Substitutable in equal amounts for dry berbere in most recipes.",
      "", "DEL-leh"),
    lambda did: v(did, "Gursha Delleh",
        ["½ cup berbere spice blend",
         "1 tsp ground roasted korarima",
         "1 tsp fine sea salt",
         "⅓ cup olive oil"],
        [("Mix dry ingredients",
          "In a small bowl, mix the berbere, korarima, and salt."),
         ("Add water and oil",
          "Add ⅓ cup water and mix. Add the olive oil and mix until well combined. Store in an airtight container in the refrigerator for up to 6 months, or freeze for up to 1 year.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=0, sv=16, sp="spicy",
        story="This deep red paste has a big advantage: because the spices are already dissolved, the flavours meld faster and much more smoothly into your food.")
))

SEED_DATA.append((
    d("Mitmita / Dukus", "ሚጥሚጣ", "condiment", "All Ethiopia",
      "Ethiopian seasoning salt — a unique blend of dried chilies, korarima, and besobela (Ethiopian basil). Essential for kitfo and a finishing touch on countless dishes.",
      "", "mit-MEE-tah"),
    lambda did: v(did, "Gursha Mitmita",
        ["½ cup whole dried red chilies",
         "¼ cup dried minced garlic",
         "¼ cup dried minced onion",
         "¼ cup ground ginger",
         "¼ cup unroasted korarima seeds",
         "¼ cup dried besobela (Ethiopian basil) or dried regular basil",
         "2 tbsp fine sea salt",
         "1 tsp ground turmeric"],
        [("Blend",
          "In a spice blender, blend everything until finely ground. Transfer to an airtight jar."),
         ("Store",
          "Store at room temperature for 6 months.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=0, sv=28, sp="spicy",
        story="Once you've tried this unique blend of flavours on meat, you won't go back to a packaged seasoned salt.")
))

SEED_DATA.append((
    d("Awaze", "አዋዜ", "condiment", "All Ethiopia",
      "Tsion Café's signature green hot sauce — a refreshing, vibrant blend of jalapeños, ginger, and cilantro. Dollop on eggs, use as a marinade, or serve alongside any cooked protein.",
      "", "ah-WAH-zeh"),
    lambda did: v(did, "Tsion Café Awaze",
        ["6–8 jalapeño peppers, roughly sliced into rounds",
         "1 yellow onion, peeled and quartered",
         "10 garlic cloves, peeled",
         "1\" piece fresh ginger, peeled and cut into pieces",
         "½ bunch fresh cilantro, leaves and thin stems, roughly chopped",
         "¾ tsp fine sea salt", "¼ tsp black pepper",
         "1 tbsp fresh lemon juice", "1 tbsp olive oil"],
        [("Blend",
          "In a food processor, pulse the jalapeños, onion, garlic, ginger, cilantro, salt, and black pepper until a chunky sauce forms. Add the lemon juice and 1 tbsp cold water and process until smooth. Add the olive oil and pulse until incorporated."),
         ("Store",
          "Transfer to an airtight container. Store in the refrigerator for up to 3 months.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=0, sv=20, sp="spicy",
        story="The signature hot sauce at Tsion Café, this refreshing mixture of jalapeños, ginger, and cilantro perks up any food.")
))

SEED_DATA.append((
    d("Hilbe / Abish", "ሕልቤ", "condiment", "Ethiopia / Yemen",
      "Fenugreek sauce — a gelatinous, tangy condiment traditionally served alongside Yemenite chicken soup, reflecting the deep cultural ties between Ethiopian and Yemenite Jews.",
      "", "HIL-beh"),
    lambda did: v(did, "Gursha Hilbe",
        ["3 tbsp ground fenugreek",
         "2 tsp zhoug (spicy green sauce)",
         "2 tsp fresh lemon juice",
         "1 tsp fine sea salt"],
        [("Soak the fenugreek",
          "In a medium bowl, mix the fenugreek and ½ cup water. Cover and let sit at room temperature until it forms a gelatinous paste, at least 1 hour and up to overnight."),
         ("Blend and store",
          "Transfer paste to a food processor. Add ½ cup water, the zhoug, lemon juice, and salt and blend until well combined. Store in the refrigerator for up to 1 week.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=0, sv=8, sp="medium",
        story="This fenugreek sauce celebrates the ties between Ethiopians and Yemenites, who often supported and married each other.")
))

SEED_DATA.append((
    d("Zhoug", "ዞግ", "condiment", "Yemen / Ethiopia",
      "Spicy green herb sauce originating in Yemen — bright, fresh, and packed with cilantro, parsley, and serrano peppers. A staple condiment at Tsion Café.",
      "", "ZOOG"),
    lambda did: v(did, "Gursha Zhoug",
        ["1 tsp cumin seeds", "1 tsp coriander seeds",
         "1 tsp green cardamom seeds", "1 tsp black peppercorns",
         "½ bunch cilantro, leaves and stems, roughly chopped",
         "½ bunch flat-leaf parsley leaves, roughly chopped",
         "6 serrano peppers, trimmed and roughly chopped",
         "8 garlic cloves, peeled", "2\" piece fresh ginger, peeled",
         "¼ cup fresh lemon juice", "¼ cup olive oil",
         "1 tsp fine sea salt"],
        [("Toast the spices",
          "Warm a small skillet over medium heat. Add the cumin, coriander, cardamom seeds, and peppercorns and toast until dark and fragrant, 1–2 minutes. Transfer to a plate to cool."),
         ("Blend",
          "In a food processor, combine the toasted seeds, cilantro, parsley, serranos, garlic, ginger, lemon juice, olive oil, and salt. Process until emulsified, about 1 minute. Store in the refrigerator for up to 1 week.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=5, sv=12, sp="spicy",
        story="This spicy green herb-filled mixture originated in Yemen and has recently become popular in the United States and the Middle East.")
))

SEED_DATA.append((
    d("Senafich", "ሰናፍጭ", "condiment", "All Ethiopia",
      "Homemade Ethiopian mustard — stronger than Western mustard with a pourable, drizzle-ready texture that deepens in flavour over time.",
      "", "seh-NAH-fich"),
    lambda did: v(did, "Gursha Senafich",
        ["½ cup mustard powder, whisked to remove lumps",
         "⅛ tsp fine sea salt", "⅛ tsp black pepper",
         "1 cup hot water, plus more if necessary"],
        [("Mix and rest",
          "Place the mustard powder, salt, and pepper in a large bowl. Slowly whisk in the hot water to give a pourable texture. Pour into an airtight jar and refrigerate for at least 1 day before using. Store in the refrigerator for up to 2 months.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=0, sv=16, sp="medium",
        story="If you've never made mustard from scratch, you'll be pleased with the strength of this one. As this sits in your refrigerator, the flavour deepens over time.")
))


# ════════════════════════════════════════════════════════════════════════════
# CHAPTER 2 — BREAD
# ════════════════════════════════════════════════════════════════════════════

SEED_DATA.append((
    d("Injera / Taita", "እንጀራ", "bread", "All Ethiopia",
      "Ethiopia's iconic spongy sourdough flatbread made from teff — both an edible plate and utensil. Naturally gluten-free when made with pure teff, with a signature tangy flavour.",
      "", "in-JEH-rah"),
    lambda did: v(did, "Gursha Classic Teff Injera",
        ["2 cups (460g) ivory teff flour",
         "2 cups (460g) brown teff flour",
         "½ tsp active dry yeast",
         "5 cups (1,200g) lukewarm water, plus more if necessary",
         "Pinch of baking powder"],
        [("Day 1 — Mix the batter",
          "In a large container with a tight-fitting lid, use your hands to combine both teff flours and yeast. Add 3 cups lukewarm water and mix aggressively until a thick batter forms with no dry lumps. Pour the remaining 2 cups lukewarm water around the sides and mix until combined. Cover and ferment in a warm room for about 24 hours."),
         ("Day 2 — Stir and ferment again",
          "Uncover: water and flour will have begun to separate. Pour off any water on top. Break up any lumps with your hands, adding up to ½ cup more lukewarm water if needed. Mix until smooth. Cover and ferment for another 24 hours."),
         ("Day 3 — Finish the batter",
          "Pour off any water on top. Add the baking powder and mix with hands or a whisk to form a smooth, pourable batter (similar to pancake batter). If too thick, add ¼ cup lukewarm water."),
         ("Cook the injera",
          "Warm a 12-inch nonstick pan over high heat, then reduce to medium. Pour about ¾ cup batter into the centre and quickly swirl to coat the entire pan. Cover and cook until small bubbles form over the entire surface, the edges are dry, and no whiteness remains, about 45 seconds. Slide a wide spatula under and carefully lift off. It should be spongy, full of holes on top, and not browned on the bottom.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=5, sv=9, sp="mild",
        notes="Makes 8–10 injera. Process takes 3 days due to fermentation. Refrigerate for up to 1 week or freeze up to 1 month.",
        story="Injera has many uses beyond a delicious flatbread. It can be an edible plate, covered with stews, or a utensil — tear off a piece and use it to scoop up meat or vegetables with your hands.")
))

SEED_DATA.append((
    d("Dabo / Hibsit", "ዳቦ", "bread", "All Ethiopia",
      "Spiced whole wheat Ethiopian Shabbat bread — fragrant with coriander, fenugreek, and cardamom. A cherished centerpiece of the Ethiopian Jewish Sabbath table.",
      "", "DAH-boh"),
    lambda did: v(did, "Avejo's Gursha Dabo",
        ["1½ tbsp ch'ew kemem (earthy seasoned salt)",
         "1½ tsp sugar", "1 tsp active dry yeast",
         "½ tsp fine sea salt", "2 cups (480g) warm water",
         "3 cups (420g) bread flour",
         "1 cup (140g) coarse whole wheat flour"],
        [("Mix the dough",
          "In a medium bowl, combine the ch'ew kemem, sugar, yeast, and sea salt. Add the warm water and stir until well combined. Add the bread flour and whole wheat flour and knead until the dough is smooth and sticky, 6–8 minutes."),
         ("First rise",
          "Shape the dough into a ball, cover the bowl with plastic wrap, place a towel on top, and let sit in a warm place until doubled in size, about 1 hour."),
         ("Second rise and bake",
          "Line a sheet pan or 9-inch baking pan with parchment paper. Punch down the dough, shape into a neat ball, and place on the prepared pan. Cover and let rise until puffed, 1–1½ hours. Preheat oven to 400°F. Bake until lightly browned, 30–40 minutes. Cool completely before serving.")],
        tags=["vegan", "dairy_free"], prep=20, cook=40, sv=12, sp="mild",
        story="Avejo Aklum is known for having very blessed hands. This dabo, adapted from her instructions, is an unusually well-seasoned, spiced version of the cherished Shabbat bread.")
))

SEED_DATA.append((
    d("Hanza", "ሃንዛ", "bread", "Tigray",
      "Layered yellow corn flatbread from Tigray — made with two types of corn over 3 days of fermentation, then filled with niter kibbeh and mitmita for a rich, fragrant result.",
      "", "HAN-zah"),
    lambda did: v(did, "Gursha Hanza",
        ["4 cups (400g) corn flour",
         "3 cups (720g) warm water",
         "1 cup (128g) coarsely ground cornmeal",
         "2 cups (260g) all-purpose flour",
         "1 tbsp sugar", "1 tbsp vegetable oil",
         "1 tsp fine sea salt", "½ tsp ground fenugreek",
         "½ tsp baking powder",
         "~10 tbsp niter kibbeh, for cooking and serving",
         "¼ cup mitmita, for serving",
         "Awaze, for serving"],
        [("Day 1 — Start the batter",
          "In a large container with a lid, mix the corn flour and warm water. Cover and let sit at room temperature for 24 hours."),
         ("Day 2 — Cook a portion and combine",
          "Divide the batter into four parts. Scoop out one-quarter and whisk into 1 cup boiling water in a small pot. Stir over medium-low heat until it pulls away from the sides, 8–10 minutes. Cool completely. To the remaining ¾ of batter, stir in cornmeal, all-purpose flour, sugar, oil, salt, fenugreek, and 1 cup water. Knead well. Add the cooled dough and another 1 cup water. Mix until smooth like thick pancake batter. Cover and keep in a cool dark place for 24 hours."),
         ("Day 3 — Cook the hanza",
          "By day 3, the batter should have varied bubbles and a yogurty smell. Whisk in ½ cup water and the baking powder — batter should be loose like drinkable yogurt. In an 8- or 9-inch nonstick skillet, ladle 1 cup batter and rotate to cover the surface. Cover with a lid and cook undisturbed for 3 minutes. Spread 2 tbsp niter kibbeh and ½ tsp mitmita over the warm hanza. Flip a second cooking hanza on top. Cook 5 more minutes, flip again, and serve.")],
        tags=["vegetarian"], prep=20, cook=10, sv=5, sp="medium",
        notes="Traditional process takes 3 days. The 'eyes' (bubbles) indicate the batter is ready.",
        story="This hanza is influenced by Beejhy's mother, who was well known for making this distinctive Tigrayan corn-based flatbread.")
))

SEED_DATA.append((
    d("Kita / Kicha", "ቂጣ", "bread", "All Ethiopia",
      "Simple Ethiopian flatbread that requires no rising or fermenting — made quickly on the road or at home. A staple of journeys and Sabbath preparation.",
      "", "KIT-ah"),
    lambda did: v(did, "Gursha Kita",
        ["2 cups (260g) all-purpose flour",
         "¼ tsp fine sea salt",
         "1½ tsp niter kibbeh, unsalted butter, or vegetable oil",
         "Optional toppings: niter kibbeh, mitmita, berbere"],
        [("Make the batter",
          "In a large bowl, use your hands to mix the flour, salt, and 1½ cups water together until the mixture becomes a thick batter."),
         ("Cook the kita",
          "Warm a large nonstick skillet over medium heat. Add ½ tsp niter kibbeh and spread to coat. Pour in about ½ cup batter and spread over the skillet surface using wet hands. Cover and steam until the top starts to look dry and the edges are defined, 2–4 minutes. Flip and cook until the bottom is golden, about 2 more minutes. Repeat with remaining batter."),
         ("Serve",
          "Serve plain, or drizzle with niter kibbeh and top with spices. Serve immediately.")],
        tags=["vegetarian"], prep=5, cook=15, sv=3, sp="mild",
        story="This is what you make when you need simple, delicious bread quickly. Even during the most harrowing moments in their journeys, the family always spent Friday afternoons preparing this flatbread to observe the Sabbath.")
))

SEED_DATA.append((
    d("Loudo", "ሉዶ", "bread", "Tigray",
      "Niger seed bread — a deeply earthy flatbread made with sorghum flour and topped with a dark, fragrant niger seed paste. An ancient Beta Israel recipe resurrected from memory.",
      "", "LOO-doh"),
    lambda did: v(did, "Gursha Loudo",
        ["½ cup niger seeds, picked over",
         "½ tsp berbere", "¾ tsp fine sea salt",
         "1 cup (140g) sorghum flour",
         "1 cup (130g) all-purpose flour",
         "½ tsp baking powder",
         "¼ tsp ch'ew kemem",
         "Vegetable oil, for greasing the pan"],
        [("Toast and grind the niger seeds",
          "Warm a medium skillet over low heat. Add niger seeds and toast, stirring constantly, until fragrant with a white-golden tinge, about 5 minutes. Cool completely. Grind in a spice grinder. Sift through a fine-mesh strainer. Combine the seed powder, berbere, ¼ tsp salt, and ¼ cup water to form a paste. Set aside."),
         ("Make the dough",
          "In a medium bowl, combine sorghum flour, all-purpose flour, baking powder, remaining ½ tsp salt, and ch'ew kemem. Add 1¼ cups cold water and knead until a dough forms."),
         ("Cook the loudo",
          "Lightly oil an 8- or 9-inch nonstick skillet and warm over low heat. Transfer all the dough to the pan and press with wet hands into an even layer. Cook until firm around the edges, about 5 minutes. Use wet hands to spread the seed paste all over the flatbread. Cover and cook until the centre is set and the edges have puffed a little, another 5 minutes. Remove and cool on a serving plate.")],
        tags=["vegan", "dairy_free"], prep=20, cook=15, sv=6, sp="mild",
        story="The moment Beejhy bites into this bread, she immediately returns to her childhood in Ethiopia and her journey to Sudan. Re-creating it felt like an important connection to the past — the resurrection of an ancient recipe.")
))

SEED_DATA.append((
    d("Kategna", "ቃጥኛ", "bread", "All Ethiopia",
      "Injera treat — crispy fried injera spread with niter kibbeh, berbere, and awaze. The Ethiopian cook's savory snack, made from the last of the injera batter.",
      "", "kah-TEN-yah"),
    lambda did: v(did, "Gursha Kategna",
        ["¼ cup niter kibbeh, melted",
         "1 tbsp berbere",
         "2 (10-inch) injera",
         "2 tsp awaze (optional)"],
        [("Mix the butter",
          "In a small bowl, mix the niter kibbeh and berbere."),
         ("Crisp the injera",
          "Warm a 12-inch nonstick pan over high heat. Lay one injera in the pan and cook until the bottom is crisp and edges are curling, about 1 minute. Transfer to a serving plate."),
         ("Top and serve",
          "Use a spoon to spread half the niter kibbeh-berbere mix over the top of the injera. Drizzle with awaze if using. Repeat with the other injera. Serve immediately.")],
        tags=["gluten_free", "vegetarian"], prep=5, cook=5, sv=2, sp="medium",
        story="My mother used to pour the last of the batter onto the hot pan, dollop on some niter kibbeh and hot sauce, sprinkle on berbere, and place it in my waiting hands — something to keep my stomach from growling until the full meal was served.")
))

SEED_DATA.append((
    d("Kolo", "ቆሎ", "snack", "All Ethiopia",
      "Crunchy Ethiopian snack mix — roasted chickpeas, wheat berries, and sunflower seeds. A beloved journey food (senki) that sustained families on the long walk to Sudan.",
      "", "KOH-loh"),
    lambda did: v(did, "Gursha Kolo",
        ["⅓ cup dried desi (small) chickpeas",
         "1 cup wheat berries",
         "¼ cup sunflower seeds",
         "¼ tsp fine sea salt",
         "Optional: ¼ cup roasted peanuts and/or golden raisins",
         "About 1 tsp mitmita or berbere (optional)"],
        [("Soak the chickpeas",
          "In a small bowl, cover the chickpeas with water by about 1 inch and soak while you prepare the rest."),
         ("Roast the wheat berries",
          "Heat a cast-iron skillet over medium heat. Add wheat berries and roast undisturbed until you hear the first pop, about 90 seconds. Stir constantly until deep golden brown, about 3 minutes. Spread on a tray to cool."),
         ("Roast the sunflower seeds",
          "Return the skillet to medium heat and add sunflower seeds. Stir constantly until dark, about 3 minutes. Spread on the tray."),
         ("Roast the chickpeas",
          "Return the skillet to medium heat. Drain the chickpeas and add to the pan. Sprinkle with sea salt and stir constantly until darkened and fragrant, about 3 minutes. Combine everything on the tray. Add peanuts/raisins if desired. Sprinkle with mitmita or berbere. Cool completely.")],
        tags=["vegan", "dairy_free"], prep=10, cook=15, sv=6, sp="mild",
        notes="Store in an airtight container at room temperature for up to 3 months.",
        story="When they had no bread during their journey to Sudan, the family munched on this while drinking coffee and pictured better days ahead in Israel.")
))


# ════════════════════════════════════════════════════════════════════════════
# CHAPTER 3 — SUNRISE SUSTENANCE (Breakfast)
# ════════════════════════════════════════════════════════════════════════════

SEED_DATA.append((
    d("Genfo / Gaat", "ጀንፎ", "breakfast", "All Ethiopia",
      "Hearty teff porridge — a thick, satisfying bowl made from teff flour, topped with a well of niter kibbeh and a dusting of berbere. Traditionally served to new brides and mothers after childbirth.",
      "", "GEN-foh"),
    lambda did: v(did, "Gursha Genfo",
        ["1 tsp fine sea salt",
         "1½ cups teff flour",
         "1 tbsp plus ¼ tsp niter kibbeh",
         "½ tsp berbere"],
        [("Boil the water",
          "In a nonstick medium pot, combine 3 cups water and the salt and bring to a boil over medium-high heat. Remove about 1 cup boiling water and set aside."),
         ("Cook the porridge",
          "Stir the teff flour into the pot, reduce heat to medium, and vigorously mix into a thick, wet paste — stirring quickly prevents lumps. Add ½ cup reserved water, mix for about 1 minute. Cover and cook 2 minutes. Add another ¼ cup water, stir, cover, and cook 2 minutes. Add the remaining ¼ cup water, stir vigorously for 1 minute. Cover and cook until the porridge looks like thick, wet dough and forms a ball, about 3 minutes."),
         ("Serve",
          "In the bottom of a medium serving bowl, place ¼ tsp niter kibbeh. Scoop the porridge on top and smooth the surface. Spoon a hole in the middle and place 1 tbsp niter kibbeh in the centre. Sprinkle berbere on top.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=20, sv=4, sp="mild",
        story="This hearty porridge represents new beginnings. It is the traditional sustenance served to new brides and pregnant women when they go into labor and then give birth.")
))

SEED_DATA.append((
    d("Ful", "ፉል", "breakfast", "All Ethiopia",
      "Stewed fava beans — protein-packed and deeply flavored with kulet and cumin, served with hard-boiled eggs, onion, jalapeño, and fresh ayib. An Ethiopian Jewish breakfast staple.",
      "", "FOOL"),
    lambda did: v(did, "Gursha Ful (Canned Bean Version)",
        ["2 (16 oz) cans fava beans, undrained",
         "¼ cup kulet (fragrant stew base)",
         "1 tsp ground cumin",
         "½ tsp fine sea salt", "½ tsp black pepper",
         "1 tbsp niter kibbeh, melted",
         "Garnishes: 2 hard-boiled eggs quartered, diced red onion, chopped jalapeño, chopped tomato, 2 tbsp ayib or crumbled feta, drizzle of niter kibbeh or olive oil",
         "Kita flatbread, for dipping"],
        [("Cook the beans",
          "In a large skillet, combine the beans and their liquid, kulet, cumin, salt, pepper, and niter kibbeh. Bring to a simmer over medium heat, stirring frequently and coarsely mashing the beans with a wooden spoon, until thickened, 8–10 minutes."),
         ("Garnish and serve",
          "Transfer to a shallow serving bowl and garnish with the eggs, onion, jalapeño, tomato, ayib, and a drizzle of niter kibbeh or olive oil. Serve with kita for dipping.")],
        tags=["gluten_free"], prep=5, cook=10, sv=8, sp="medium",
        story="Here are two ways to use the nutritious, protein-packed fava beans that Beejhy ate for breakfast as a child. This canned bean version cuts more than an hour off the process.")
))

SEED_DATA.append((
    d("Enqulal Tibs / Enquaquho Tibsi", "እንቁላል ጥብስ", "breakfast", "All Ethiopia",
      "Scrambled eggs with tomato, red onion, and jalapeño — a hearty, vegetable-filled Ethiopian breakfast seasoned with berbere and turmeric. Best served with injera.",
      "", "en-KOO-lal tibs"),
    lambda did: v(did, "Gursha Enqulal Tibs",
        ["1 tbsp olive oil",
         "¼ cup minced jalapeño",
         "¼ cup minced red onion",
         "¼ cup diced tomato",
         "4 large eggs",
         "¼ tsp berbere",
         "Pinch of ground turmeric",
         "⅛ tsp fine sea salt", "⅛ tsp black pepper",
         "¼ tsp niter kibbeh or butter (optional), for drizzling",
         "Injera (optional), for serving"],
        [("Sauté the vegetables",
          "In a large nonstick skillet, warm the oil over medium heat. Add the jalapeño, onion, and tomato and sauté until just softened, about 2 minutes."),
         ("Scramble the eggs",
          "In a medium bowl, beat the eggs, berbere, turmeric, salt, and black pepper. Add to the skillet and scramble until cooked through. Drizzle with niter kibbeh if desired. Serve over injera.")],
        tags=["gluten_free", "vegetarian"], prep=5, cook=10, sv=4, sp="medium",
        story="Instead of making an omelet, try this hearty vegetable-filled scrambled eggs with Ethiopian flavors. It's very nutritious and can keep you filled up well into the day.")
))

SEED_DATA.append((
    d("Kinche", "ቅንጨ", "breakfast", "All Ethiopia",
      "Savory steel-cut oat porridge — a warming Ethiopian breakfast, traditionally made with bulgur wheat. Served with niter kibbeh melted on top and a sprinkle of berbere.",
      "", "KIN-cheh"),
    lambda did: v(did, "Gursha Kinche",
        ["1 tbsp vegetable oil",
         "¼ tsp fine sea salt",
         "2 cups steel-cut oats, rinsed until water runs nearly clear",
         "¼ cup niter kibbeh, melted",
         "½ jalapeño, finely chopped",
         "½ tsp berbere"],
        [("Cook the oats",
          "In a medium pot, combine 3 cups water, the oil, and salt and bring to a boil over medium heat. Add the oats, cover, reduce the heat to low, and simmer, stirring occasionally, until tender and the water is absorbed, about 45 minutes."),
         ("Serve",
          "Transfer to a serving bowl. Drizzle the niter kibbeh on top and garnish with the jalapeño and berbere. Serve warm.")],
        tags=["vegetarian", "dairy_free"], prep=5, cook=45, sv=4, sp="mild",
        story="For the Beta Israel community, breakfast is not sweet — and that includes porridge. This savory oatmeal is the breakfast ideal.")
))

SEED_DATA.append((
    d("Atmit / Sibko", "አጥሚት", "breakfast", "All Ethiopia",
      "Banana flour porridge — a thin, nourishing drink-soup made from bula (enset/false banana powder) and oat flour. Warming, comforting, and traditionally given to new mothers and the unwell.",
      "", "AHT-meet"),
    lambda did: v(did, "Gursha Atmit",
        ["¼ cup oat flour",
         "2 tsp bula (banana flour from enset plant)",
         "2 tbsp honey (optional)",
         "Pinch of ground cinnamon (optional)"],
        [("Blend the oat flour",
          "In a small bowl, whisk together the oat flour and 1 cup water until well combined, about 1 minute."),
         ("Start the porridge",
          "In a small pot, bring 1½ cups water to a boil over high heat. Pour the oat/water mixture through a fine-mesh strainer into the pot. Stir well, bring to a boil, reduce heat to medium-low, and simmer until slightly thickened, about 5 minutes."),
         ("Add bula and finish",
          "In a small bowl, whisk the bula with ½ cup water. Slowly stream into the pot, whisking constantly. Increase heat to medium and cook until vigorously bubbling and a gravy-like consistency, about 5 minutes. Serve hot, topped with honey or cinnamon if desired.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=15, sv=2, sp="mild",
        notes="Bula can be mail-ordered or found at Ethiopian grocery stores.",
        story="This thin, nutritious porridge is made with the powdered root of the enset plant, also known as false banana — an enormous crop in Ethiopia. A delicious way to stay warm in wintertime, or to nourish yourself when feeling under the weather.")
))

SEED_DATA.append((
    d("Dabo Fit-Fit", "ዳቦ ፍትፍት", "breakfast", "All Ethiopia",
      "Crumbled Shabbat bread mixed with sour cream, Ethiopian salad, and spices — the Beta Israel Saturday morning breakfast. A cherished tradition of assembling your own bowl from the spread.",
      "", "DAH-boh fit-fit"),
    lambda did: v(did, "Gursha Dabo Fit-Fit",
        ["4½ cups nay kedam dabo (pot-baked Shabbat bread), broken into bite-sized pieces",
         "1 cup sour cream or plain yogurt",
         "1 cup nay habesha selata (colorful Ethiopian chopped salad)",
         "1 tbsp niter kibbeh",
         "1 tsp berbere",
         "½ tsp fine sea salt, plus more to taste",
         "½ tsp black pepper, plus more to taste"],
        [("Combine and serve",
          "In a large bowl, mix the bread pieces with the sour cream, Ethiopian salad, niter kibbeh, berbere, salt, and pepper. Mix gently. Taste and adjust the seasoning, if necessary.")],
        tags=["vegetarian"], prep=5, cook=0, sv=4, sp="mild",
        story="Dabo fit-fit is what the Beta Israel community eats for breakfast on Saturday morning after synagogue. Some of the most cherished childhood memories are of going to sleep on Friday in great anticipation of this breakfast, then awakening on Saturday morning to a spread of salads and bread pieces.")
))

SEED_DATA.append((
    d("Injera Fir-Fir", "እንጀራ ፍርፍር", "breakfast", "All Ethiopia",
      "Ripped injera tossed with kulet stew base and niter kibbeh — the quick, satisfying Ethiopian breakfast of leftover injera given new life.",
      "", "in-JEH-rah fir-FIR"),
    lambda did: v(did, "Gursha Injera Fir-Fir",
        ["½ cup kulet (fragrant stew base)",
         "2 (10-inch) injera, torn into bite-sized pieces",
         "2 tsp niter kibbeh",
         "Fine sea salt and black pepper",
         "2 tsp diced tomato", "2 tsp diced jalapeño",
         "2 tbsp ayib, plain yogurt, or sour cream"],
        [("Warm the kulet",
          "In a large skillet, warm the kulet over medium heat until sizzling. Add the injera and mix until evenly coated and warmed through."),
         ("Finish and garnish",
          "Mix in the niter kibbeh and salt and pepper to taste. Add the tomato and jalapeño and sauté until softened, about 2 minutes. Garnish with the ayib, yogurt, or sour cream.")],
        tags=["gluten_free"], prep=5, cook=10, sv=4, sp="medium",
        story="Here's a quick, simple preparation of fir-fir for when you have leftover injera.")
))


# ════════════════════════════════════════════════════════════════════════════
# CHAPTER 4 — VEGETABLES
# ════════════════════════════════════════════════════════════════════════════

SEED_DATA.append((
    d("Gomen / Hamli", "ጎመን", "main", "All Ethiopia",
      "Braised collard greens — gently cooked with onion, garlic, ginger, and jalapeño. A traditional accompaniment to doro wot, providing a mellow foil to rich, spicy stews.",
      "", "GOH-men"),
    lambda did: v(did, "Gursha Gomen",
        ["1 cup vegetable oil",
         "1 red onion, diced",
         "2 tsp minced garlic", "1 tsp minced fresh ginger",
         "2 lb collard greens, washed, thick stems removed, leaves finely chopped",
         "1½ tsp fine sea salt", "½ tsp black pepper",
         "¼ tsp ground nutmeg",
         "1 jalapeño, cut lengthwise into four long pieces"],
        [("Sauté the aromatics",
          "In a medium pot, warm the oil over medium heat. Add the onion and sauté, stirring occasionally, until softened, about 5 minutes. Add the garlic and ginger and sauté until lightly browned and fragrant, about 10 minutes."),
         ("Braise the greens",
          "Add the collard greens, salt, and pepper. Cook uncovered, stirring occasionally, until the greens are dark green and tender, about 30 minutes. If greens start to scorch, add water, a few tablespoons at a time."),
         ("Finish",
          "Taste and adjust salt and pepper. Stir in the nutmeg and the jalapeño slices.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=45, sv=8, sp="mild",
        story="Gomen makes Beejhy think of her grandmother, who used to grow a very soft, delicate type of wild greens in Ethiopia and was delighted to find a similar green while foraging after settling in Israel.")
))

SEED_DATA.append((
    d("Ye Tikil Gomen Alicha / Caulo", "የጥቅል ጎመን አልጫ", "main", "All Ethiopia",
      "Music-in-your-mouth cabbage with potatoes and carrots — a mild, fragrant stew built on a dry-sautéed onion base, finished with fresh ginger, garlic, and korarima.",
      "", "yeh ti-KIL GOH-men ah-LEE-chah"),
    lambda did: v(did, "Gursha Tikil Gomen",
        ["3 carrots, peeled, halved lengthwise, sliced into ½-inch half-moons",
         "2 white potatoes, peeled, cut into bite-sized pieces",
         "2 yellow onions, sliced into thin half-moons",
         "½ cup vegetable oil",
         "1 tsp ground turmeric",
         "¾ tsp fine sea salt", "¾ tsp black pepper",
         "1 head green cabbage (~1½–2 lb), cored and cut into 1-inch strips",
         "1 tbsp ginger/garlic paste (or 2 tsp minced garlic + 1 tsp minced ginger)",
         "1 jalapeño, trimmed and cut lengthwise into 4 strips",
         "½ tsp ground roasted korarima"],
        [("Soak vegetables",
          "In a large bowl, cover the carrots and potatoes with cold water and soak while you prepare the other ingredients."),
         ("Dry-sauté the onions",
          "In a large deep pot with no oil, sauté the onions over medium heat until beginning to soften, 2–3 minutes. Add the oil."),
         ("Cook carrots and potatoes",
          "Drain the carrots and potatoes and add them to the pot. Cover and cook, stirring constantly, about 5 minutes. Stir in the turmeric, salt, and pepper. Cover and cook, stirring occasionally, until the carrots and potatoes are tender, about 5 minutes."),
         ("Add cabbage and finish",
          "Mix in the cabbage, cover, and cook, stirring occasionally, until the cabbage has shrunk and softened, about 15 minutes. Stir in the garlic/ginger mixture, jalapeño, and korarima. Cover and cook until soft and fragrant, 5–10 minutes. Taste and adjust seasoning.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=40, sv=8, sp="mild",
        story="This mild stew owes its deep, satisfying flavour to a few special techniques. Adding the ginger and garlic at the very end means they cook just slightly from residual heat, keeping them bright and fresh.")
))

SEED_DATA.append((
    d("Fasolia", "ፋሶሊያ", "side", "All Ethiopia",
      "Fragrant green beans and carrots — sautéed with onion, ginger, garlic, cumin, and korarima until deeply flavored and tender. A classic Ethiopian vegetable side dish.",
      "", "fah-SOH-lee-yah"),
    lambda did: v(did, "Gursha Fasolia",
        ["4 medium carrots, peeled, quartered lengthwise, cut into 2-inch sticks",
         "½ cup vegetable oil",
         "1 medium red onion, sliced into thin half-moons",
         "1 tbsp minced fresh ginger", "1 tbsp minced garlic",
         "½ tsp salt, plus more to taste",
         "2 lb green beans, trimmed and cut into 2–3 inch pieces",
         "1 tsp ground cumin",
         "1 tsp ground roasted korarima"],
        [("Prep the carrots",
          "Set the carrots aside in cold water until ready to use."),
         ("Sauté aromatics",
          "In a large skillet, warm the oil over medium heat. Add the onion, ginger, garlic, and salt and sauté until the onion is softened, about 4 minutes. Drain the carrots and add to the skillet. Cook until the carrots are softened but not cooked through, about 5 minutes."),
         ("Cook the beans",
          "Stir in the green beans. Cover the skillet and cook undisturbed for 5 minutes. Uncover and stir in the cumin and korarima. Sauté until the beans are dark green and blistered and the carrots are soft, adding about ½ cup water and scraping the bottom to avoid burning, 10–20 minutes. Serve warm or at room temperature.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=30, sv=8, sp="mild",
        story="While simple to prepare, this dish is so much better than the usual steamed green beans and carrots. It's imbued with roasted ground korarima, which lends a powerful, uniquely Ethiopian flavour.")
))

SEED_DATA.append((
    d("Alicha Wot / Alicha Tsebhi", "አልጫ ወጥ", "main", "All Ethiopia",
      "Mild vegetable stew — potatoes, carrots, and zucchini simmered in a golden turmeric and oil base with a gentle warmth from jalapeño. Avejo Aklum's signature variation.",
      "", "ah-LEE-chah wot"),
    lambda did: v(did, "Avejo's Gursha Alicha Wot",
        ["1 medium red onion, chopped",
         "6 garlic cloves, minced",
         "5 medium russet potatoes, peeled, cut into 1-inch chunks",
         "3 large carrots, peeled and diced",
         "1 jalapeño or serrano pepper, roughly chopped with seeds",
         "½ cup hot water", "⅓ cup olive oil",
         "1 tbsp chicken or vegetable bouillon powder",
         "1 tsp ground turmeric", "1 tsp sweet paprika",
         "2 tsp fine sea salt", "1 tsp black pepper",
         "½ tsp ground roasted korarima",
         "½ tsp ground cumin",
         "3 medium zucchini, peeled and cut into 1-inch chunks",
         "Injera, for serving"],
        [("Dry-sauté the aromatics",
          "In a dry medium pot, sauté the onion over low heat for 3 minutes. Add the garlic and cook until the onion is translucent, 5–10 minutes."),
         ("Simmer the vegetables",
          "Stir in the potatoes, carrots, jalapeño, hot water, oil, bouillon powder, turmeric, paprika, salt, black pepper, korarima, and cumin. Cover and cook, stirring occasionally, just until the potatoes are tender, about 15 minutes."),
         ("Add zucchini and serve",
          "Add the zucchini and simmer just until tender, 5–10 minutes. Taste and adjust salt. Serve over injera.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=35, sv=6, sp="mild",
        story="Traditionally, Ethiopian vegetable stew is based around cabbage, carrots, and potatoes, but cousin Avejo Aklum swaps the cabbage for zucchini, adding just a bit of heat from berbere for her signature stew.")
))

SEED_DATA.append((
    d("Bamya", "ባምያ", "main", "All Ethiopia",
      "Okra stew with tomatoes — tender okra chunks in a cumin-and-berbere spiced tomato sauce. Inspired by time spent in Sudan, with none of the slimy texture of overcooked okra.",
      "", "BAM-yah"),
    lambda did: v(did, "Gursha Bamya",
        ["½ cup vegetable oil",
         "1 small red onion, diced", "6 garlic cloves, chopped",
         "1½ tsp berbere", "1 tsp ground cumin",
         "3 tomatoes, diced",
         "1 lb okra, trimmed and cut into 1-inch pieces",
         "½ tsp fine sea salt", "½ tsp black pepper",
         "¼ tsp ground roasted korarima",
         "Injera or rice, for serving"],
        [("Sauté aromatics",
          "In a large pot, heat the oil over medium heat. Add the onion and garlic and sauté until the onions are translucent and garlic is beginning to brown, about 5 minutes."),
         ("Cook the tomatoes",
          "Stir in the berbere and cumin. Add the tomatoes and cook, stirring occasionally, until they break down into a saucy consistency, 10–12 minutes. Add up to 1½ cups water if they start to stick."),
         ("Add okra and finish",
          "Mix in the okra, salt, and pepper. Reduce heat to medium-low, cover, and simmer, stirring occasionally, until the okra is tender and starting to split, 10–15 minutes. Stir in the korarima and simmer 5 minutes to blend flavours. Serve with injera or rice.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=35, sv=4, sp="medium",
        story="I wanted to pay tribute to my time in Sudan by creating an okra stew that had none of the slimy, mushy texture I remember from childhood. I cut the okra into chunks and cook just until tender.")
))

SEED_DATA.append((
    d("Dubba Wot / Dubba Tsebhi", "ዱባ ወጥ", "main", "All Ethiopia",
      "Pumpkin stew with date honey — kabocha squash simmered in a spiced tomato base with silan (date honey). Ethiopian and Israeli cooking traditions coming together in one warming vegetarian stew.",
      "", "DOO-bah wot"),
    lambda did: v(did, "Gursha Dubba Wot",
        ["1 medium red onion, chopped",
         "½ cup olive oil",
         "1 (6 oz) can tomato paste",
         "1 tbsp + 1 tsp minced garlic",
         "2 tsp minced fresh ginger",
         "6 cups hot water",
         "2 tbsp delleh or berbere",
         "1–2 tbsp silan (date honey), to taste",
         "2 tsp fine sea salt", "1 tsp black pepper",
         "½ tsp ground roasted korarima",
         "4 lb kabocha or butternut squash, peeled and cut into ½-inch cubes",
         "Injera, for serving"],
        [("Build the base",
          "In a large dry pot, sauté the onion over medium heat, stirring constantly, until translucent, about 3 minutes. Add the oil, tomato paste, garlic, ginger, and ½ cup hot water and bring to a simmer. Stir in the delleh, silan, salt, pepper, and korarima."),
         ("Add squash and cook",
          "Stir in the squash and remaining 5½ cups hot water. Reduce heat to low, cover, and cook, stirring occasionally, until the pumpkin is tender, about 25 minutes. Serve on top of injera.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=35, sv=8, sp="medium",
        story="When Genet was growing up in Ethiopia, dates were considered candy, and anything sweet was rarely consumed. Upon moving to Israel, the family found that the silan cuts the spice: The more you add, the less spicy the stew will be.")
))

SEED_DATA.append((
    d("Inigudayi Tibs / Kantishala Tibsi", "እንጉዳይ ጥብስ", "main", "Tigray",
      "Sautéed mushrooms with rosemary — wild mushrooms cooked in niter kibbeh with red wine, berbere, and korarima. Inspired by childhood foraging in the forests of Tigray.",
      "", "in-GOO-die tibs"),
    lambda did: v(did, "Gursha Inigudayi Tibs",
        ["1 red onion, sliced into half-moons",
         "8 oz Baby Bella or any mushrooms, wiped clean and sliced",
         "1 cup red wine, plus more if needed",
         "2 tbsp niter kibbeh",
         "1 sprig fresh rosemary",
         "1 large jalapeño (optional), sliced into thick rings",
         "¾ tsp minced garlic", "¼ tsp minced fresh ginger",
         "1 tsp berbere", "1 tsp awaze",
         "½ tsp fine sea salt", "½ tsp black pepper",
         "1 tomato, cut into bite-sized pieces",
         "1 tsp ground roasted korarima"],
        [("Sauté",
          "Warm a large dry skillet over medium heat. Add the onion and sauté until slightly softened, 1–2 minutes. Stir in the mushrooms, red wine, 1 tbsp niter kibbeh, the rosemary, jalapeño (if using), garlic, ginger, berbere, awaze, salt, and pepper. Sauté, adding 1 tbsp more wine at a time if the mixture starts to stick, until the mushrooms are softened, about 10 minutes."),
         ("Finish",
          "Stir in the tomato, the remaining 1 tbsp niter kibbeh, and the korarima and sauté for 5 more minutes. Serve immediately.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=20, sv=4, sp="medium",
        story="In March/April and September/October each year, mushrooms grew wild in the forested, hilly area near where Beejhy grew up in Tigray. This dish still evokes the thrill of foraging as a child.")
))

SEED_DATA.append((
    d("Qey Sir / Qeyh Sur", "ቀይ ስር", "side", "All Ethiopia",
      "Braised beets — vibrant, tender beets simmered with cumin, garlic, ginger, and cilantro. Served hot or cold. Symbolic on the Rosh Hashanah table as a sign of fresh beginnings.",
      "", "KAY sir"),
    lambda did: v(did, "Gursha Qey Sir",
        ["6 beets, washed and trimmed",
         "⅓ cup vegetable oil",
         "1 yellow onion, diced",
         "2 tsp minced garlic",
         "1 tsp minced fresh ginger",
         "½ tsp ground cumin",
         "¼ tsp fine sea salt", "¼ tsp black pepper",
         "¼ bunch fresh cilantro, chopped",
         "1 jalapeño (optional), chopped"],
        [("Boil the beets",
          "In a large pot, combine the beets with water to cover. Bring to a boil and cook until tender, 45 minutes to 1 hour. Drain and let cool slightly. Peel and cut into bite-sized cubes."),
         ("Sauté and combine",
          "In a large wide pot, heat the oil, onion, garlic, and ginger over medium heat. Stir, lowering the heat if the onion begins to brown, until softened and fragrant, about 5 minutes. Stir in the beets, cumin, salt, pepper, cilantro, and jalapeño if using. Cover and cook about 5 minutes to let the flavours integrate. Taste and adjust seasoning.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=60, sv=12, sp="mild",
        story="The Hebrew word for beet, selek, has the same root word as the phrase for 'driven out of something,' so when we place beets on the celebratory Rosh Hashanah table, it's symbolic of starting fresh.")
))

SEED_DATA.append((
    d("Tsion Café's Shakshuka", "ሻክሹካ", "breakfast", "All Ethiopia",
      "Poached eggs in tomato sauce — the beloved Middle Eastern classic given an Ethiopian soul with berbere and colorful bell peppers. A bestseller and Today Show feature at Tsion Café.",
      "", "shak-SHOO-kah"),
    lambda did: v(did, "Tsion Café Shakshuka",
        ["½ cup vegetable oil",
         "1 yellow onion, diced", "6 garlic cloves, minced",
         "1 small red bell pepper, diced",
         "1 small green bell pepper, diced",
         "1 (28 oz) can diced tomatoes, undrained",
         "½ jalapeño (optional, for more heat)",
         "1–1½ tsp berbere, to taste",
         "1 tsp ground cumin", "1 tsp ground paprika",
         "¾ tsp fine sea salt", "¼ tsp black pepper",
         "½ bunch fresh cilantro, chopped",
         "4–6 large eggs",
         "1 tbsp crumbled feta cheese"],
        [("Build the sauce",
          "In a medium cast-iron skillet, warm the oil over medium-low heat. Add the onion and garlic and sauté until soft, about 10 minutes. Add the bell peppers and sauté until soft, about 10 minutes. Add the tomatoes, jalapeño if using, berbere, cumin, paprika, salt, and black pepper. Simmer, stirring occasionally, until the tomatoes have broken down, about 15 minutes."),
         ("Add cilantro",
          "Add the cilantro (reserving a tablespoon for garnish) and stir. Taste and adjust."),
         ("Poach the eggs",
          "Increase heat to medium. Using a spoon, make 4–6 wells in the tomatoes. Add 1 egg to each well. Cook uncovered until the egg whites become cloudy, 2–3 minutes. Cover and cook until the yolks are runny (about 4 minutes) or firm (about 6 minutes). Remove from heat and garnish with reserved cilantro and feta cheese.")],
        tags=["vegetarian", "gluten_free"], prep=10, cook=35, sv=6, sp="medium",
        story="As a single woman in my twenties, living alone in Harlem, often arriving home from work late at night and finding a near-bare refrigerator, I found that shakshuka was a savior. Mine is unique: The berbere gives it a sultry kick that keeps my customers coming back.")
))

SEED_DATA.append((
    d("Diniche Alicha / Dinish Alicha", "ድንች አልጫ", "main", "All Ethiopia",
      "Red potato stew with turmeric and jalapeño — a simple, delicately flavored golden stew. Dry-sautéed onions concentrate the flavor, with jalapeño added at the end for gentle heat.",
      "", "din-EECH ah-LEE-chah"),
    lambda did: v(did, "Gursha Diniche Alicha",
        ["1 large or 2 small yellow onions, halved and thinly sliced",
         "½ cup vegetable oil",
         "2 tsp minced garlic", "1 tsp minced fresh ginger",
         "1 tsp ground turmeric",
         "2 lb red potatoes, unpeeled, cut into 1-inch cubes",
         "1 lb carrots, peeled, cut on the bias into ½-inch slices",
         "1½ tsp fine sea salt", "½ tsp black pepper",
         "1 large jalapeño, quartered lengthwise"],
        [("Dry-sauté the onions",
          "In a dry medium Dutch oven or heavy-bottomed pot, stir the onions over medium heat. When they start to sizzle after about 3 minutes, add the oil and sauté, stirring frequently, until the onions soften, 6–8 minutes. Stir in the garlic, ginger, and turmeric and cook until bright yellow, about 5 minutes."),
         ("Cook the vegetables",
          "Add the potatoes, carrots, salt, pepper, and ½ cup water. Cover and cook, stirring frequently, until the potatoes are tender, 15–20 minutes, adding up to ½ cup more water if needed."),
         ("Add jalapeño and serve",
          "Stir in the jalapeño, cover, and cook, stirring occasionally, to infuse the flavours, about 5 minutes. Taste and adjust.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=35, sv=8, sp="mild",
        story="This is a simple, delicately flavored potato stew that goes nicely with non-spicy meat dishes. The dry-sautéeing technique concentrates the onion flavour beautifully.")
))


# ════════════════════════════════════════════════════════════════════════════
# CHAPTER 5 — LEGUMES AND GRAINS
# ════════════════════════════════════════════════════════════════════════════

SEED_DATA.append((
    d("Shiro", "ሽሮ", "main", "All Ethiopia",
      "Silky chickpea stew — a beloved hallmark of Ethiopian cuisine made from shiro powder (dried chickpea flour and spices) or whole canned chickpeas, simmered with berbere and aromatics.",
      "", "SHEE-roh"),
    lambda did: v(did, "Gursha Shiro (Powder Method)",
        ["½ cup vegetable oil",
         "2 tsp minced garlic",
         "1 tsp minced fresh ginger",
         "1 cup shiro powder",
         "½ tsp fine sea salt", "½ tsp black pepper",
         "¼ tsp ground cumin (optional)"],
        [("Start the base",
          "In a medium pot, warm the oil over medium heat. Add the garlic and ginger, mix for about 1 minute, then add 2⅔ cups water and whisk well until thoroughly combined, about 2 minutes."),
         ("Cook the shiro",
          "Add the shiro powder, salt, pepper, and cumin if using. Whisk vigorously to smooth the mixture and simmer, stirring constantly, until very thick, 8–10 minutes. Taste and adjust.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=5, cook=15, sv=4, sp="medium",
        story="Shiro is a beloved hallmark of Ethiopian cuisine. The most common way to make it is from shiro powder — a dried mix of chickpea flour and spices — which is quick, convenient and life-sustaining. Many Beta Israel abstain from dairy and milk on Wednesdays and Fridays, and turn to this staple.")
))

SEED_DATA.append((
    d("Beejhy's Shiro", "ቢጂ ሽሮ", "main", "All Ethiopia",
      "Silky chickpea stew using canned chickpeas — Beejhy Barhany's version developed when shiro powder was impossible to find in the United States. Blended to a luxuriously creamy consistency.",
      "", "SHEE-roh"),
    lambda did: v(did, "Beejhy's Canned Chickpea Shiro",
        ["4 medium red onions, quartered, soaked briefly in water, drained",
         "1 tbsp minced fresh ginger",
         "1 tbsp minced garlic",
         "¾ cup vegetable oil",
         "3 tbsp berbere",
         "2½ tsp fine sea salt", "2 tsp black pepper",
         "1 (6 oz) can tomato paste",
         "4 (15.5 oz) cans chickpeas, undrained"],
        [("Make the onion paste",
          "In a food processor, process the onions, ginger, and garlic to make a thick paste. Pour into a large pot, bring to a simmer over medium heat, and cook until most of the water has evaporated, 5–10 minutes."),
         ("Build the spiced base",
          "Stir in the oil and simmer for another 10 minutes. Stir in the berbere, 2 tsp salt, and 1½ tsp pepper. Simmer, stirring and scraping constantly, until deep red and thickened, 15–20 minutes. Add the tomato paste and cook until melted in, 15–20 minutes."),
         ("Blend and combine",
          "In a clean food processor, blend the chickpeas and their liquid until smooth and creamy, about 5 minutes. Pour into the pot. Add remaining ½ tsp salt and ½ tsp pepper. Bring to a simmer and cook, stirring frequently and adding water if necessary, until creamy and silky, 25–30 minutes.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=75, sv=12, sp="medium",
        story="When Beejhy first moved to the United States, shiro powder was nearly impossible to find. Going without this beautiful, nutritious chickpea stew was simply not an option for her.")
))

SEED_DATA.append((
    d("Messer Wot / Birsen Tsebhi", "ምስር ወጥ", "main", "All Ethiopia",
      "Slow-cooked red lentil stew — deeply flavored with berbere, onion paste, and korarima. The appeal of lentil stew goes back to Biblical times. A cornerstone of Ethiopian fasting cuisine.",
      "", "MES-er wot"),
    lambda did: v(did, "Gursha Messer Wot",
        ["4 medium red onions, quartered, soaked briefly in water, drained",
         "1 tbsp minced garlic",
         "1 tbsp minced fresh ginger",
         "¾ cup vegetable oil, plus more as needed",
         "3 tbsp berbere",
         "1½ tsp fine sea salt", "1½ tsp black pepper",
         "1 (6 oz) can tomato paste",
         "3 cups red lentils, rinsed well",
         "1 tsp ground roasted korarima (or ground cardamom)"],
        [("Make the onion paste base",
          "In a food processor, process the onions, garlic, and ginger into a thick paste. Pour into a large pot and bring to a simmer over medium heat. Cook, stirring occasionally, until most liquid has evaporated, 5–10 minutes."),
         ("Add oil and berbere",
          "Add the oil and simmer for another 10 minutes. Stir in the berbere, salt, and pepper. Simmer, stirring and scraping constantly, until deep red and thickened and the onions are melting together, 15–20 minutes."),
         ("Add tomato paste",
          "Add the tomato paste. Fill half the empty can with water, scrape the sides, and add to the pot. Boil and simmer until the tomato paste melts in, 15–20 minutes."),
         ("Cook the lentils",
          "Stir in the lentils and 4 cups water. Simmer 10 minutes. Add 1 cup water and cook until lentils begin to disintegrate into the stew, about 10 minutes longer. Stir in the korarima. Taste and adjust.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=75, sv=8, sp="spicy",
        story="While red lentils cook much more quickly than other types, taking our time helps them develop the right flavour and texture. Feel free to add more berbere.")
))

SEED_DATA.append((
    d("Kik Alicha / Ater Alicha", "ክክ አልጫ", "main", "All Ethiopia",
      "Sunny yellow split pea stew — mild, golden, and versatile. Spread on bread, use as a dip, dollop on salad, or serve as part of a bountiful Ethiopian spread. Freezes beautifully.",
      "", "kik ah-LEE-chah"),
    lambda did: v(did, "Gursha Kik Alicha",
        ["2 cups dried yellow split peas",
         "2 yellow onions, very finely chopped",
         "2 tsp minced garlic", "1 tsp minced fresh ginger",
         "½ cup vegetable oil",
         "2 tsp fine sea salt", "2 tsp black pepper",
         "1 tsp ground turmeric",
         "1 jalapeño, halved lengthwise and seeded",
         "Injera or cooked rice, for serving"],
        [("Soak the peas",
          "Soak split peas in cold water for 5–10 minutes. Pick them over and wash several times until water is only mildly cloudy."),
         ("Dry-cook aromatics",
          "In a large dry pot, cook the onions, garlic, and ginger over medium heat, stirring gently, until the water mostly evaporates and the mixture looks dry, about 5 minutes. Stir in the oil and cook, stirring occasionally, for 5 minutes."),
         ("Cook the stew",
          "Stir in the salt, pepper, and turmeric. Stir in the split peas and 5 cups water. Cover and simmer, stirring about every 5 minutes, until peas are soft and the stew is thick and saucy, about 45 minutes. Stir in the jalapeño. Serve over injera or with rice.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=55, sv=8, sp="mild",
        story="This mild stew is so versatile — you can spread it on bread, use it as a dip, dollop it on a salad, or just serve it as part of a bountiful Ethiopian spread.")
))

SEED_DATA.append((
    d("Avejo's Timtimo", "ትምቲሞ", "main", "Tigray",
      "Mild fava and yellow split pea stew — Avejo Aklum's unique blend of two legumes, blended silky smooth. Rich and creamy in a way that rivals even shiro.",
      "", "tim-TEE-moh"),
    lambda did: v(did, "Avejo's Gursha Timtimo",
        ["2 cups dried split fava beans, well rinsed",
         "1 cup dried yellow split peas, well rinsed",
         "2 medium red onions, diced",
         "6 garlic cloves, minced",
         "1 tbsp grated fresh ginger",
         "1½ tsp salt", "½ tsp black pepper",
         "½ cup olive oil",
         "2 tbsp delleh or berbere",
         "1 cup hot water",
         "¼ tsp ground roasted korarima",
         "Injera, for serving"],
        [("Cook the legumes",
          "In a medium pot, combine the fava beans and split peas, add water to cover by 1–2 inches. Bring to a boil, skim foam, reduce to a simmer, and cook until tender, 30–40 minutes. Drain, reserving the bean water."),
         ("Build the sauce",
          "In a food processor, blend the onions, garlic, and ginger until a paste. Pour into the pot and cook over medium heat, stirring constantly, for 5 minutes. Add the salt and pepper and cook until water evaporates, about 3 minutes. Stir in the olive oil, delleh, and hot water. Bring to a boil, cover, and cook, stirring occasionally, until the sauce comes together, 10–12 minutes."),
         ("Blend the legumes and combine",
          "In a clean food processor, blend the cooked beans and 2 cups bean water until smooth and creamy, adding up to 1 cup more water if needed. Mix the bean purée into the pot, add the korarima, reduce heat to low, and cook 5 minutes to blend flavours. Serve on top of injera.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=60, sv=6, sp="mild",
        story="Kik Alicha is typically made with just one type of bean, but that was too simple for aunt Avejo Aklum. Her unique blend of fava beans and yellow split peas results in a silky, creamy mixture that rivals even shiro.")
))

SEED_DATA.append((
    d("Sambusa", "ሳምቡሳ", "snack", "All Ethiopia",
      "Savory fried lentil pockets — crispy triangular pastries filled with seasoned lentils, onion, and jalapeño. A popular street food and appetizer across Africa and the Middle East.",
      "", "sam-BOO-sah"),
    lambda did: v(did, "Gursha Sambusa",
        ["1 cup cooked brown or green lentils, at room temperature",
         "¼ red onion, finely diced",
         "½ jalapeño (optional), chopped",
         "Fine sea salt", "Squeeze of lemon juice (optional)",
         "2 tbsp all-purpose flour",
         "2 (12-inch) flour tortillas, each cut into 6 equal wedges",
         "Vegetable oil, for frying",
         "Awaze (optional), for dipping"],
        [("Make the filling",
          "In a medium bowl, mix together the lentils, onion, jalapeño, salt to taste, and lemon juice if using."),
         ("Make the flour paste",
          "In a small bowl, mix the flour and 2 tbsp water into a paste, adding more water 1 tsp at a time if necessary."),
         ("Fill and fold",
          "Microwave the tortilla wedges for 15 seconds to soften. Place one wedge on a work surface, point facing away. Fold the two closer corners inward to meet in the middle. Seal with flour paste into a cone shape. Hold the cone and fill with a heaping tbsp of lentil filling. Brush the pointed tip with flour paste, fold it down to create a triangle, and press edges to seal. Repeat."),
         ("Fry",
          "In a large cast-iron skillet, heat about ½ inch of oil to 350°F. Working in batches, fry the sambusa, flipping once, until deep golden brown, 2–3 minutes per side. Serve with awaze as a dipping sauce if desired.")],
        tags=["vegan", "dairy_free"], prep=20, cook=20, sv=12, sp="medium",
        story="This fried snack and appetizer is one of Beejhy's favourite ways to use up leftover cooked lentils or stew. Using a tortilla instead of dough makes it simple.")
))

SEED_DATA.append((
    d("My Grandmother's Black-Eyed Peas and Barley Stew", "ምስር የሐምሌ", "main", "All Ethiopia",
      "Simple, nutritious, wholesome stew of black-eyed peas and barley with kulet and ayib. This was Beejhy's grandmother's last meal request before she died.",
      "", ""),
    lambda did: v(did, "Gursha Black-Eyed Peas and Barley Stew",
        ["10 oz dried black-eyed peas",
         "3 tsp fine sea salt",
         "½ cup hulled barley",
         "¼ cup olive oil",
         "1 small red onion, chopped",
         "¼ cup kulet (fragrant stew base)",
         "1 tbsp ayib (fresh Ethiopian cheese)",
         "1 tsp niter kibbeh, melted",
         "Cooked rice (optional), for serving"],
        [("Cook the peas and barley",
          "In a medium pot, combine the peas, water to cover, and 1 tsp salt. Bring to a boil and cook until tender, about 55 minutes. Drain. In another pot, combine barley, water to cover, and 1 tsp salt. Bring to a boil and cook until tender, about 55 minutes, adding water if the pot becomes dry. Drain."),
         ("Make the stew",
          "In a medium pot, warm the oil over medium heat. Add the onion and sauté until softened, about 5 minutes. Add the kulet and stir, then add the cooked peas, barley, remaining 1 tsp salt, and 1 cup water. Simmer uncovered, stirring occasionally, until most water is absorbed and the mixture is a thick stew, about 15 minutes. Garnish with ayib and niter kibbeh. Serve with rice if desired.")],
        tags=["gluten_free"], prep=10, cook=75, sv=4, sp="mild",
        story="Simple, nutritious, wholesome, comforting, and gently spiced with Ethiopian flavours: My grandmother requested this for her last meal before she died.")
))

SEED_DATA.append((
    d("Hummus with Spicy Silsi", "ሁሙስ", "side", "Ethiopia / Israel",
      "Ethiopian-Israeli fusion hummus — blended chickpeas with tahini and berbere, topped with a vibrant kulet stew base. Inspired by Mali Aklum and her mother Samira.",
      "", "HOO-moos"),
    lambda did: v(did, "Gursha Hummus with Spicy Silsi",
        ["2 (15.5 oz) cans chickpeas, liquid drained and reserved",
         "3 large garlic cloves, roughly chopped",
         "Juice of 1 lemon (3–4 tbsp)",
         "2 tbsp well-mixed tahini",
         "½ tsp berbere",
         "½ tsp fine sea salt", "¼ tsp black pepper",
         "1 cup cold or room temperature kulet",
         "2 boiled eggs (optional), quartered, for garnish",
         "Injera chips or pita, for serving"],
        [("Blend the hummus",
          "In a food processor, combine the chickpeas, garlic, lemon juice, tahini, berbere, salt, and pepper. Blend until smooth, adding about 3 tbsp of the chickpea liquid, 1 tbsp at a time, to create a smooth, creamy, airy mixture, about 3 minutes."),
         ("Serve",
          "Transfer to a large shallow serving bowl. Smooth so it is higher on the sides with a divot in the centre. Spoon the kulet into the middle. Garnish with the eggs and serve with injera chips or pita.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=0, sv=8, sp="medium",
        story="This hummus combines the hummus that the family learned to make in their new home of Israel with the fiery flavours of Ethiopia. Mali remembers it as a special treat after a long day of cooking chicken stew.")
))

SEED_DATA.append((
    d("Azifa Salad", "አዚፋ", "salad", "All Ethiopia",
      "Refreshing lentil salad — cool cooked lentils tossed with onion, jalapeño, mustard, and cilantro. Light, nutritious, and ideal for breaking fasts or warm weather meals.",
      "", "ah-ZEE-fah"),
    lambda did: v(did, "Gursha Azifa Salad",
        ["2 cups brown or green lentils, rinsed",
         "1 tbsp vegetable oil",
         "1 red onion, finely diced",
         "Juice of 1 lime or lemon, plus more to taste",
         "½ bunch fresh cilantro, finely chopped",
         "1 large jalapeño, minced",
         "¼ cup senafich (Ethiopian mustard) or Dijon mustard",
         "½ tsp ground cumin",
         "½ tsp fine sea salt", "¼ tsp black pepper"],
        [("Cook the lentils",
          "In a large pot, combine the lentils, oil, and 4 cups water. Bring to a boil and cook until tender, about 30 minutes. Drain, spread onto a large tray, and cool to room temperature."),
         ("Mix and marinate",
          "In a large bowl, mix the onion with the lime juice and let sit for at least 10 minutes. Add the cooled lentils, cilantro, jalapeño, mustard, cumin, salt, and black pepper and stir to combine. Taste and adjust. Refrigerate for at least 20 minutes to allow flavours to blend. Serve chilled or at room temperature.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=10, cook=30, sv=10, sp="medium",
        story="As a child, Beejhy remembers eating many cool lentil salads like this one. Not only are they ideal for warm weather, their light, nutritious nature makes them perfect for breaking fasts.")
))

SEED_DATA.append((
    d("Tsion Café's Jollof Rice", "ጆሎፍ ሩዝ", "main", "West Africa / Ethiopia",
      "Ethiopian-spiced Jollof rice — the classic West African one-pot rice dish given an Ethiopian soul with berbere. A beloved bestseller at Tsion Café during the pandemic.",
      "", "JOL-off rice"),
    lambda did: v(did, "Tsion Café Jollof Rice",
        ["4 plum tomatoes, cut into chunks",
         "3 large carrots, peeled and cut into chunks",
         "2 large yellow onions, cut into chunks",
         "2 large jalapeños, quartered lengthwise",
         "6 garlic cloves, peeled",
         "3\" chunk fresh ginger, peeled",
         "1 cup vegetable oil",
         "1 tbsp berbere",
         "1 tbsp chicken or vegetable bouillon powder",
         "1½ tsp fine sea salt", "1½ tsp black pepper",
         "1 tsp curry powder", "¼ tsp dried thyme",
         "3 cups parboiled long-grained rice"],
        [("Make the purée",
          "In a food processor, blend the tomatoes, carrots, onions, jalapeños, garlic, and ginger into a rough purée (in 2 batches if needed). Pour into a large pot, add about ½ cup water to rinse the processor, and add to the pot."),
         ("Cook down and add oil",
          "Place the pot over medium heat and cook, stirring occasionally, until the water has mostly evaporated, about 25 minutes. Stir in the oil and simmer until fully integrated, about 30 minutes."),
         ("Season and add rice",
          "Stir in the berbere, bouillon powder, salt, black pepper, curry powder, and thyme and cook for about 5 minutes. Rinse the rice once, then mix into the sauce. Reduce heat to medium-low, cover, and cook undisturbed for 5 minutes."),
         ("Finish",
          "Mix in 1 cup water, cover, and cook undisturbed until the rice is tender and a dark, crispy layer has formed on the bottom, about 20 minutes. Serve warm.")],
        tags=["vegan", "gluten_free", "dairy_free"], prep=15, cook=80, sv=8, sp="medium",
        story="After an employee from Nigeria taught Beejhy his favourite version of this classic West African rice dish, she immediately added it to the menu of Tsion Café. During the pandemic, they made enormous pots, selling it as takeout and donating thousands of portions to the hungry.")
))


# ════════════════════════════════════════════════════════════════════════════
# CHAPTER 6 — MEAT AND FISH
# ════════════════════════════════════════════════════════════════════════════

SEED_DATA.append((
    d("Doro Wot / Derho Tsebhi", "ዶሮ ወጥ", "main", "All Ethiopia",
      "Ethiopia's national dish — a deeply spiced chicken drumstick stew simmered in kulet with whole boiled eggs. The presence of doro wot signifies a rite of passage or special occasion.",
      "", "DOH-roh wot"),
    lambda did: v(did, "Gursha Doro Wot",
        ["2 lb chicken drumsticks (8–10), skinned",
         "2 tbsp fresh lemon juice",
         "1 tbsp fine sea salt",
         "8 large eggs",
         "6 cups kulet (fragrant stew base)"],
        [("Soak the drumsticks",
          "In a large bowl, combine the drumsticks, lemon juice, and salt. Add cold water to cover and swish to mix. Soak for at least 10 minutes and up to 1 hour."),
         ("Boil the eggs",
          "In a medium pot, cover the eggs with cold water. Bring to a boil and cook for 8 minutes. Transfer to an ice bath. Peel the eggs, leaving whole. Make four shallow cuts from top to bottom on each egg, scoring the white but stopping at the yolk."),
         ("Heat the kulet",
          "In a large pot, heat the kulet over medium heat, stirring occasionally, until simmering."),
         ("Cook the chicken",
          "Drain the water from the drumsticks. Wash well under running water, massaging and rinsing several times. Submerge in the kulet. Bring back to a simmer and cook gently, stirring occasionally, until drumsticks are completely cooked through, 25–30 minutes. During the last 5 minutes, add the eggs and gently stir to submerge in sauce. Serve warm.")],
        tags=["gluten_free", "dairy_free"], prep=20, cook=45, sv=8, sp="spicy",
        story="Doro wot is perhaps the most well-known Ethiopian dish. The mere presence of this rich, fiery chicken stew signifies a rite of passage or a special occasion. Cutting up a whole chicken for doro wot is among the first skills that Ethiopian Jewish mothers teach their daughters.")
))

SEED_DATA.append((
    d("Doro Wot Alicha", "ዶሮ ወጥ አልጫ", "main", "All Ethiopia",
      "Golden chicken drumstick stew — a mild version of doro wot for those sensitive to heat. Flavored with turmeric, cumin, and korarima instead of berbere.",
      "", "DOH-roh wot ah-LEE-chah"),
    lambda did: v(did, "Gursha Doro Wot Alicha",
        ["2 lb chicken drumsticks (~10), skinned",
         "2 tbsp fresh lemon juice",
         "1 tbsp + 2½ tsp fine sea salt",
         "4 yellow onions, quartered",
         "1 cup vegetable oil",
         "½ tsp ground turmeric",
         "1 jalapeño, quartered lengthwise",
         "2 tsp minced garlic", "1 tsp minced fresh ginger",
         "1 tsp ground cumin",
         "¼ tsp ground roasted korarima",
         "5 hard-boiled eggs, halved"],
        [("Soak the drumsticks",
          "In a large bowl, combine drumsticks, lemon juice, 1 tbsp salt, and cold water to cover. Soak for at least 10 minutes and up to 1 hour."),
         ("Cook the onions",
          "In a food processor, blend the onions until smooth. Warm a dry Dutch oven over medium heat. Add the onions, bring to a simmer, and cook, stirring frequently, until most water has evaporated, 30–35 minutes. Add the oil and turmeric and mix constantly until well combined, about 5 minutes."),
         ("Cook the chicken",
          "Drain and wash the drumsticks well. Add to the pot and cook, stirring frequently, for 10 minutes. Add 2 cups water and remaining 2½ tsp salt and stir frequently until chicken is almost cooked through, 5–10 minutes."),
         ("Finish",
          "Add the jalapeño, garlic, ginger, cumin, and korarima and simmer, stirring occasionally, until flavours are integrated and chicken is cooked through, about 10 minutes. Taste and adjust salt. Garnish with the eggs.")],
        tags=["gluten_free", "dairy_free"], prep=20, cook=65, sv=5, sp="mild",
        story="This is doro wot for those who are sensitive to heat. It leaves out the berbere and relies on small amounts of turmeric, cumin, and korarima to enhance the chicken.")
))

SEED_DATA.append((
    d("Kai Wot / Zigni", "ቃይ ወጥ", "main", "All Ethiopia",
      "Traditional spicy, hearty beef stew — blazing with berbere and rich with slow-cooked beef chuck. Kai wot means 'red stew' in Amharic. A must at special occasions and a Shabbat centrepiece.",
      "", "KAI wot"),
    lambda did: v(did, "Gursha Kai Wot",
        ["4–5 medium red onions, cut into chunks, blended in a food processor",
         "1 cup vegetable oil",
         "⅓ cup berbere",
         "2 tsp minced garlic", "1 tsp minced fresh ginger",
         "2 lb beef chuck, cut into ¼-inch cubes",
         "Juice of ½ lemon",
         "1 tsp fine sea salt",
         "1 cup warm water, plus more as needed",
         "½ tsp ground roasted korarima",
         "¼ cup niter kibbeh (optional), melted"],
        [("Build the onion base",
          "In a dry saucepan, simmer the onions over medium heat until most water has evaporated, about 10 minutes. Add the oil, berbere, garlic, and ginger. Reduce heat to medium-low and simmer, stirring occasionally, for 5 minutes."),
         ("Add the beef",
          "In a large bowl, mix the chuck with the lemon juice and rinse with cold water, pouring off blood and impurities. Add the beef and salt to the pan, cover, and simmer, stirring frequently, until beef is cooked through, about 15 minutes."),
         ("Low and slow",
          "Add the warm water and korarima. Continue simmering until the meat collapses and becomes meltingly tender, 45 minutes to 1 hour, adding more warm water when necessary (½ cup at a time) to keep the sauce loose and moist. Taste and adjust salt. Drizzle with niter kibbeh and serve warm.")],
        tags=["gluten_free", "dairy_free"], prep=20, cook=80, sv=8, sp="spicy",
        story="Blazing with flavour and color, kai wot is a must at many special occasions and a beautiful addition to the Shabbat table. This is Beejhy's favourite way to make it, using beef chuck and a healthy amount of berbere.")
))

SEED_DATA.append((
    d("Sega Tibs / Sega Tibsi", "ሰጋ ጥብስ", "main", "All Ethiopia",
      "Tender sautéed beef — quick weeknight beef tenderloin pan-seared with niter kibbeh, mitmita, rosemary, and tej wine. Honoring the tradition of families sharing a butchered cow.",
      "", "SEH-gah tibs"),
    lambda did: v(did, "Gursha Sega Tibs",
        ["1 tbsp + 1½ tsp niter kibbeh",
         "1 lb beef tenderloin, cut into bite-sized cubes",
         "½ tsp fine sea salt", "½ tsp black pepper",
         "½ red onion, sliced into half-moons",
         "½ jalapeño, cut into thin long strips",
         "¼ tsp minced fresh ginger", "¼ tsp minced garlic",
         "1 tsp mitmita (or 2 tsp berbere)",
         "1 sprig fresh rosemary",
         "¼ cup tej (Ethiopian honey wine), white wine, or another sweet wine",
         "½ tomato, cut into bite-sized pieces"],
        [("Sear the beef",
          "In a large skillet, warm 1 tbsp niter kibbeh over medium heat. Add the beef, salt, and pepper and brown on all sides, about 1 minute. Add the onion, jalapeño, ginger, garlic, mitmita, and rosemary and sauté for about 2 minutes."),
         ("Deglaze and finish",
          "Pour in the wine, scraping the bottom of the skillet, and sauté until the meat is tender, adding 1 tbsp water at a time if necessary to keep the mixture saucy, 8–10 minutes. Add the tomato and sauté until softened, about 2 minutes. Drizzle with the remaining 1½ tsp niter kibbeh. Serve immediately.")],
        tags=["gluten_free", "dairy_free"], prep=10, cook=15, sv=4, sp="medium",
        story="This dish honours the tradition of about ten Ethiopian families getting together to split a butchered cow, the fresh meat divided equally according to a process called querecha. Make this only with the best-quality beef you can find.")
))

SEED_DATA.append((
    d("Kitfo", "ክትፎ", "main", "All Ethiopia",
      "Ethiopian beef tartare canapés — finely chopped beef tenderloin mixed with hot niter kibbeh and mitmita, served on crispy injera rounds. Ethiopia's beloved raw beef dish.",
      "", "kit-FOH"),
    lambda did: v(did, "Gursha Kitfo",
        ["1 (10-inch) injera cut into 10 small rounds, or 10 large injera chips",
         "1 lb beef tenderloin, preferably grass-fed",
         "½ cup niter kibbeh, butter, or ghee",
         "1 tsp mitmita",
         "½ tsp ground roasted korarima",
         "¼ tsp fine sea salt", "⅛ tsp black pepper",
         "Gomen (braised collard greens), for garnish (optional)",
         "Ayib or feta cheese, for garnish (optional)"],
        [("Toast the injera rounds",
          "Cut the injera into 10 small rounds 2 inches across. Toast on both sides in a dry pan until crisp but pliable, about 2 minutes."),
         ("Mince the beef",
          "Finely chop the beef as finely as possible in a food processor, meat grinder, or by hand."),
         ("Mix with hot niter kibbeh",
          "In a medium pot, warm the niter kibbeh over medium heat. Reduce heat to the barest minimum and add the beef tenderloin, mitmita, korarima, salt, and pepper. Stir vigorously to combine."),
         ("Assemble and serve",
          "Immediately spoon onto the injera rounds. If desired, garnish with gomen and ayib.")],
        tags=["gluten_free", "dairy_free"], prep=15, cook=5, sv=10, sp="medium",
        notes="The key to exceptional kitfo is starting with HOT niter kibbeh and mixing the beef quickly. Do all preparation in advance to allow for quick assembly.",
        story="The secret to making exceptional Ethiopian kitfo is starting with hot niter kibbeh and mixing the beef quickly. This is cherished by non-Jewish Ethiopians and is a showstopper canapé at any gathering.")
))

SEED_DATA.append((
    d("Beg Wot / Begi Tsebhi", "በግ ወጥ", "main", "All Ethiopia",
      "Holiday lamb stew — fall-apart lamb loin chops simmered in a rich kulet base. Served on Passover and Rosh Hashanah to commemorate the Torah-mandated sacrifice of the paschal lamb.",
      "", "beg wot"),
    lambda did: v(did, "Gursha Beg Wot",
        ["3 lb bone-in lamb loin chops",
         "Juice of ½ lemon",
         "2 cups kulet (fragrant stew base)",
         "2 tsp minced garlic", "1 tsp minced fresh ginger",
         "1 tsp fine sea salt",
         "½ tsp ground roasted korarima",
         "¼ cup niter kibbeh (optional)"],
        [("Soak and prepare the lamb",
          "Put the lamb chops in a large bowl, add the lemon juice and cold water to cover. Swish for several minutes, then soak about 10 minutes. Slice the majority of the lamb meat off the chops and cut into 1-inch pieces."),
         ("Build the stew",
          "In a large dry pot, combine the lamb meat, meaty bones, and kulet. Stir frequently over medium heat until the meat is lightly browned and the kulet begins to caramelize on the bottom, 10–15 minutes."),
         ("Slow cook to tenderness",
          "Add the garlic and ginger and cook, stirring frequently, until fragrant, 2–3 minutes. Add 2 cups water and the salt. Scrape any mixture from the bottom. Reduce heat to medium-low and cook until the meat is soft, tender, and falling apart, 30–40 minutes. Add the korarima and niter kibbeh if using. Cook 5–10 minutes more to integrate flavours.")],
        tags=["gluten_free", "dairy_free"], prep=15, cook=60, sv=8, sp="spicy",
        notes="You can substitute goat (fiyel in Amharic) as is traditional in Ethiopia. If in doubt, cook longer — falling-apart meat is crucial.",
        story="Lamb is a staple on the holiday tables of so many Jewish families. We Beta Israel serve this aromatic dish to commemorate the Torah-mandated sacrifice of the paschal lamb on Passover.")
))

SEED_DATA.append((
    d("Doro Tibs / Derho Tibsi", "ዶሮ ጥብስ", "main", "All Ethiopia",
      "Sautéed chicken with butter and herbs — boneless chicken thighs marinated in lemon, garlic, and herbs, then quickly pan-cooked with niter kibbeh, delleh, and white wine.",
      "", "DOH-roh tibs"),
    lambda did: v(did, "Gursha Doro Tibs",
        ["½ cup fresh lemon juice",
         "1 red onion, minced",
         "1 tbsp minced garlic",
         "½ tsp dried oregano", "½ tsp dried basil",
         "2 lb boneless, skinless chicken thighs",
         "1 tbsp niter kibbeh",
         "2 sprigs fresh thyme",
         "2 tbsp delleh or berbere",
         "1 tsp fine sea salt", "1 tsp black pepper",
         "⅓ cup white wine",
         "½ jalapeño, cut into long strips",
         "¾ tsp minced garlic", "¼ tsp minced fresh ginger",
         "½ tomato, cut into bite-sized pieces"],
        [("Marinate the chicken",
          "In a large bowl, whisk together the lemon juice, half the onion, garlic, oregano, and basil. Add chicken thighs and turn to coat. Cover and marinate for at least 30 minutes at room temperature or up to overnight in the refrigerator."),
         ("Cook",
          "Remove the chicken and cut into bite-sized cubes. Discard the marinade. Warm a large skillet over medium heat. Add the chicken, niter kibbeh, thyme sprigs, delleh, salt, and black pepper. Sauté for 1 minute, then add the wine and sauté until reduced, 2–3 minutes."),
         ("Finish",
          "Add the remaining onion, the jalapeño, garlic, and ginger and simmer, stirring, until the liquid mostly evaporates, red oil bubbles throughout, and chicken is cooked through and tender, 10–12 minutes. Add the tomato and sauté for about a minute. Serve immediately.")],
        tags=["gluten_free", "dairy_free"], prep=35, cook=20, sv=8, sp="medium",
        story="Here's another weeknight meal that comes together quickly. Marinate boneless, skinless chicken thighs in the morning, then throw this together for dinner later.")
))

SEED_DATA.append((
    d("Yemenite Chicken Soup", "የዬሜን ዶሮ ሾርባ", "main", "Ethiopia / Yemen",
      "A deeply flavored chicken soup seasoned with hawaij — the warming Yemenite spice blend. Adapted from Dr. Ephraim Isaac's recipe, celebrating the ties between Ethiopian and Yemenite Jewish communities.",
      "", ""),
    lambda did: v(did, "Gursha Yemenite Chicken Soup",
        ["1 whole chicken (4–5 lb), cut into 8–12 pieces, or 4–5 lb drumsticks",
         "¼ cup fresh lemon juice",
         "2 tbsp fine sea salt",
         "8 small red or white onions, peeled and left whole",
         "4 large carrots, peeled, cut into ½-inch rounds",
         "1 cup chopped celery",
         "10 garlic cloves, chopped",
         "½ cup chopped fresh parsley",
         "¼ cup + 2 tbsp chopped fresh cilantro",
         "3 tbsp hawaij (Yemenite spice mix)",
         "1 tbsp black pepper",
         "For serving: lemon wedges, hilbe, and zhoug"],
        [("Prepare the chicken",
          "In a large bowl, massage the chicken with lemon juice and 1 tbsp salt. Let sit at room temperature for at least 5 minutes and up to 30 minutes. Rinse well."),
         ("Initial boil",
          "Place the chicken in a large stockpot and add cold water to cover by 1–2 inches. Cover and bring to a boil over high heat. Uncover and boil, skimming foam periodically, for about 30 minutes."),
         ("Add vegetables and spices",
          "Add the onions, carrots, celery, garlic, parsley, ¼ cup cilantro, the hawaij, remaining 1 tbsp salt, and the pepper. Reduce heat to medium and simmer uncovered until the soup is a deep yellow, 30–45 minutes. Taste and adjust seasoning. Serve with lemon wedges, hilbe, and zhoug.")],
        tags=["gluten_free", "dairy_free"], prep=20, cook=75, sv=8, sp="medium",
        story="I adapted this deeply flavoured chicken soup from my dear friend Dr. Ephraim Isaac, a prominent half-Ethiopian, half-Yemenite academic and leader. I would love for it to be one of the first dishes that Americans think of when they think of 'Jewish foods.'")
))

SEED_DATA.append((
    d("Assa Wot / Assa Tsebhi", "ዓሳ ወጥ", "main", "All Ethiopia",
      "Shabbat fish stew — meaty fish cubes seared in niter kibbeh and simmered in kulet. A Friday night tradition carried from Ethiopia to Israel to Harlem.",
      "", "AH-sah wot"),
    lambda did: v(did, "Gursha Assa Wot",
        ["1½ lb skinless salmon fillets (or halibut, sea bass), cut into 1-inch cubes",
         "¾ tsp fine sea salt", "¼ tsp black pepper",
         "2 tbsp niter kibbeh",
         "2¼ cups kulet (fragrant stew base), warm or at room temperature"],
        [("Season and sear the fish",
          "Season the fish with salt and pepper. In a medium cast-iron skillet, warm the niter kibbeh over medium-low heat. Add the fish cubes in a single layer and sauté on all sides until lightly browned, 2–3 minutes."),
         ("Simmer in kulet",
          "Add the kulet, making sure it covers all of the fish. Reduce heat to low and simmer, gently stirring, until the fish is cooked through, 2–3 minutes. Serve warm.")],
        tags=["gluten_free", "dairy_free"], prep=10, cook=10, sv=6, sp="spicy",
        story="I associate this fish stew with marking the Shabbat during my early childhood in Ethiopia. My grandmother would walk to the market, buy the freshest fish, and make assa wot ahead of time to savor during the quiet, sacred hours between sundown Friday and sundown Saturday.")
))

SEED_DATA.append((
    d("Berbere Fried Fish", "ቤርቤሬ ዓሳ", "main", "All Ethiopia",
      "Berbere-spiced fried tilapia — crispy fillets dredged in a berbere and cumin flour coating. A fusion of Ethiopian spices and Harlem's beloved fish fry tradition.",
      "", "BER-beh-reh fried fish"),
    lambda did: v(did, "Gursha Berbere Fried Fish",
        ["Juice of 1 lemon",
         "8 tilapia fillets (6 oz each)",
         "½ cup all-purpose flour",
         "¼ cup berbere",
         "1 tsp ground cumin",
         "½ tsp fine sea salt", "½ tsp black pepper",
         "2 large eggs",
         "Vegetable oil, for frying"],
        [("Soak the fish",
          "In a bowl, combine the lemon juice and water. Add the fish fillets and gently swish around. Soak for 10 minutes, then drain."),
         ("Prepare coatings",
          "On a shallow plate, whisk together the flour, berbere, cumin, salt, and pepper. In a wide, shallow bowl, beat the eggs. Set a wire rack in a sheet pan."),
         ("Fry",
          "Pour 1 inch of oil into a large cast-iron skillet or Dutch oven and heat over medium heat until 280°F. Dip one piece of fish in the eggs (shake off excess), then in the seasoned flour (coat both sides, shake off excess). Place in the oil and fry until cooked through and golden brown, flipping halfway, 2–3 minutes per side. Drain on the rack. Continue with remaining fish.")],
        tags=["dairy_free"], prep=15, cook=30, sv=8, sp="spicy",
        story="This one combines the flavours of Beejhy's childhood home of Ethiopia with the fried fish that's so popular in her adult home of Harlem. Historians say the tradition of African American fish fries originated because enslaved people were given Saturday to themselves.")
))

SEED_DATA.append((
    d("Berbere Stuffed Peppers with Ground Chicken and Bulgur", "የቤርቤሬ ሚሚቻ", "main", "Ethiopia / Israel",
      "Charred poblano or cubanelle peppers stuffed with spiced ground chicken, bulgur, and berbere. Inspired by Asefash Mesele's tradition of stuffing peppers with beef and rice.",
      "", ""),
    lambda did: v(did, "Gursha Berbere Stuffed Peppers",
        ["¾ cup bulgur",
         "Fine sea salt",
         "10 poblano or cubanelle peppers, tops trimmed and seeded",
         "1 small red onion, chopped",
         "1 tbsp minced fresh ginger", "3 garlic cloves, minced",
         "8 oz ground chicken",
         "2 tbsp olive oil", "3 tomatoes, roughly chopped",
         "2 tbsp berbere",
         "Juice of ½ lime",
         "2 tbsp chopped fresh parsley",
         "2 tbsp chopped fresh cilantro",
         "1 tsp ground cumin"],
        [("Cook the bulgur",
          "In a small pot, combine the bulgur with water to cover and a pinch of salt. Bring to a boil, cover, and cook until tender, 10–12 minutes. Drain off any excess water."),
         ("Char the peppers",
          "Carefully char the peppers on all sides over an open flame until lightly blackened, about 3 minutes. Place in a greased 9×13-inch baking dish. Preheat oven to 350°F."),
         ("Make the filling",
          "In a dry medium skillet, sauté the onion over medium heat until translucent, about 4 minutes. Add ginger and garlic and cook 3 minutes. Add chicken, olive oil, and 2 tsp salt and sauté, breaking up the chicken, until cooked through, 5–7 minutes. Add tomatoes and cook down until saucy, about 5 minutes. Stir in the cooked bulgur, berbere, lime juice, parsley, cilantro, and cumin."),
         ("Stuff and bake",
          "Fill each pepper with ¼ to ⅓ cup of filling. Bake until peppers are tender when pierced with a knife, about 20 minutes. Serve warm.")],
        tags=["dairy_free"], prep=20, cook=45, sv=10, sp="medium",
        story="My inspiration was Asefash Mesele, who was born in Tigray and was one of the first Ethiopians to settle in Israel in the 1960s. Asefash loves to stuff peppers with beef and rice. I envisioned a healthier version with ground chicken and bulgur.")
))

SEED_DATA.append((
    d("Spicy Tomato Tilapia", "ቲላፒያ ወጥ", "main", "Ethiopia / Israel",
      "Tilapia simmered in a spiced tomato sauce — Rishan Mesele's Friday night Shabbat fish. A blend of Ethiopian berbere and Israeli flavors with serrano pepper and cilantro.",
      "", ""),
    lambda did: v(did, "Gursha Spicy Tomato Tilapia",
        ["6 plum tomatoes, chopped",
         "½ cup olive oil",
         "1 medium red onion, thinly sliced",
         "1 serrano pepper, minced",
         "8 garlic cloves, sliced",
         "2 tbsp chopped fresh cilantro, plus more for garnish",
         "2 tbsp chopped fresh parsley",
         "3 tbsp tomato paste",
         "1 tsp fine sea salt", "½ tsp black pepper",
         "½ tsp ground cumin",
         "1 tbsp chicken bouillon powder",
         "1 tbsp sweet paprika", "1 tbsp berbere",
         "½ tsp cayenne pepper (optional)",
         "6 skinless tilapia fillets (6 oz each)"],
        [("Make the sauce",
          "In a medium saucepan, cook the tomatoes over medium-low heat until soft and beginning to break down, 8–10 minutes. Add the olive oil and onion and cook until translucent, about 4 minutes. Add serrano and garlic and simmer until softened, 5–7 minutes. Mix in the cilantro, parsley, tomato paste, salt, black pepper, cumin, bouillon powder, paprika, berbere, and cayenne if using. Add 1 cup water and simmer until thickened, about 15 minutes."),
         ("Cook the fish",
          "Taste and adjust the salt. Add the tilapia, coating with the sauce, and simmer without moving the fish until cooked through, about 30 minutes. Serve garnished with cilantro.")],
        tags=["gluten_free", "dairy_free"], prep=15, cook=55, sv=6, sp="medium",
        story="My aunt Rishan Mesele loves to make this zesty fish dish on the Sabbath. In Israel, it's common to have a fish dish on Friday night. Rishan combines tilapia with Ethiopian flavours to give it a taste of our birthplace.")
))



# ════════════════════════════════════════════════════════════════════════════
# SEED RUNNER
# ════════════════════════════════════════════════════════════════════════════

async def seed():
    print(">> Seeding Gursha cookbook recipes into MongoDB...")
    inserted_dishes = 0
    inserted_variations = 0
    skipped = 0

    for dish_doc, variation_factory in SEED_DATA:
        # Skip if dish with this slug already exists
        existing = await dishes_col.find_one({"slug": dish_doc["slug"]})
        if existing:
            print(f"  [SKIP] '{dish_doc['name']}' (already exists)")
            skipped += 1
            continue

        # Insert dish
        result = await dishes_col.insert_one(dish_doc)
        dish_id = result.inserted_id
        inserted_dishes += 1

        # Insert variation
        var_doc = variation_factory(dish_id)
        await vars_col.insert_one(var_doc)
        inserted_variations += 1

        # Update variation_count on the dish
        await dishes_col.update_one(
            {"_id": dish_id},
            {"$set": {"variation_count": 1}}
        )

        print(f"  [OK] Inserted: {dish_doc['name']}")

    print(f"\nDone! {inserted_dishes} dishes and {inserted_variations} variations inserted. {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
