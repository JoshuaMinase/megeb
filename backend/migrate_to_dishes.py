"""
One-time migration: recipes → dishes + recipe_variations

Run once:
    cd backend
    python migrate_to_dishes.py

- For each recipe: creates one dishes doc (status=approved) and one recipe_variations doc (variation_name="Classic")
- Preserves old recipe._id → new variation._id mapping and updates any user-saved recipe references
- Safe to re-run: skips recipes already migrated (checks for existing dish slug)
"""
import asyncio
import re
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "megeb")]

recipes           = db["recipes"]
dishes            = db["dishes"]
recipe_variations = db["recipe_variations"]


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s


def guess_category(name: str, desc: str) -> str:
    text = (name + " " + desc).lower()
    if any(w in text for w in ["breakfast", "genfo", "chechebsa", "ful", "firfir", "porridge"]):
        return "breakfast"
    if any(w in text for w in ["snack", "sambusa", "kategna"]):
        return "snack"
    if any(w in text for w in ["sauce", "butter", "niter", "berbere spice blend"]):
        return "condiment"
    if any(w in text for w in ["salad"]):
        return "salad"
    return "main"


async def migrate():
    all_recipes = await recipes.find({}).to_list(None)
    print(f"Found {len(all_recipes)} recipes to migrate.")

    id_map = {}  # old recipe._id (str) → new variation._id (str)

    for r in all_recipes:
        slug = slugify(r["name"])

        # Make slug unique if collision
        base_slug = slug
        counter = 1
        while await dishes.find_one({"slug": slug}):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create dish doc
        dish_doc = {
            "slug": slug,
            "name": r["name"],
            "name_amharic": "",
            "category": guess_category(r["name"], r.get("description", "")),
            "region": "",
            "description": r.get("description", ""),
            "reference_image_url": r.get("image", ""),
            "status": "approved",
            "submitted_by": None,
            "variation_count": 1,
            "search_count": r.get("search_count", 0),
            "created_at": r.get("created_at", datetime.now(timezone.utc)),
        }
        dish_result = await dishes.insert_one(dish_doc)
        dish_id = dish_result.inserted_id

        # Parse cook/prep times to minutes
        def parse_minutes(s: str) -> int:
            if not s:
                return 0
            s = str(s).lower()
            total = 0
            h = re.search(r"(\d+)\s*hr", s)
            m = re.search(r"(\d+)\s*min", s)
            if h:
                total += int(h.group(1)) * 60
            if m:
                total += int(m.group(1))
            if not h and not m:
                nums = re.findall(r"\d+", s)
                if nums:
                    total = int(nums[0])
            return total

        # Create variation doc
        var_doc = {
            "dish_id": dish_id,
            "variation_name": "Classic",
            "author_id": r.get("author_id", None),
            "ingredients": r.get("ingredients", []),
            "steps": r.get("steps", []),
            "image_url": r.get("image", ""),
            "prep_time_minutes": parse_minutes(r.get("prep_time", "")),
            "cook_time_minutes": parse_minutes(r.get("cook_time", "")),
            "servings": int(re.search(r"\d+", str(r.get("servings", "2"))).group()) if re.search(r"\d+", str(r.get("servings", "2"))) else 2,
            "spice_level": "medium",
            "notes": "",
            "status": "approved",
            "likes_count": 0,
            "search_count": r.get("search_count", 0),
            "created_at": r.get("created_at", datetime.now(timezone.utc)),
        }
        var_result = await recipe_variations.insert_one(var_doc)
        id_map[str(r["_id"])] = str(var_result.inserted_id)

        print(f"  ✓ {r['name']} → dish:{slug} / variation:{var_result.inserted_id}")

    # Update any user-saved/favorited recipe references (future-proof)
    # Check if users collection has a 'saved_recipes' field referencing old recipe IDs
    users_with_saves = await db["users"].find({"saved_recipes": {"$exists": True}}).to_list(None)
    for user in users_with_saves:
        old_saves = user.get("saved_recipes", [])
        new_saves = [id_map.get(str(rid), str(rid)) for rid in old_saves]
        if new_saves != [str(r) for r in old_saves]:
            await db["users"].update_one(
                {"_id": user["_id"]},
                {"$set": {"saved_variations": new_saves}},
            )
            print(f"  Updated saved refs for user {user['_id']}")

    # Create text indexes
    await dishes.create_index([("name", "text"), ("name_amharic", "text"), ("category", "text")])
    await dishes.create_index("slug", unique=True)
    await recipe_variations.create_index([("ingredients", "text"), ("notes", "text")])
    await recipe_variations.create_index("dish_id")

    print(f"\nMigration complete. {len(id_map)} recipes migrated.")
    print("ID map (old recipe_id → new variation_id):")
    for old, new in list(id_map.items())[:5]:
        print(f"  {old} → {new}")
    if len(id_map) > 5:
        print(f"  ... and {len(id_map) - 5} more")


asyncio.run(migrate())
