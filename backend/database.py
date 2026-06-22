from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "megeb")]

users   = db["users"]
recipes = db["recipes"]
searches = db["searches"]
dishes = db["dishes"]
recipe_variations = db["recipe_variations"]
pantry = db["pantry"]
nutrition_logs = db["nutrition_logs"]
meal_plans = db["meal_plans"]
collections = db["collections"]