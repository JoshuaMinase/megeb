from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection with SSL/TLS configuration for Atlas
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Add TLS configuration for MongoDB Atlas
if "mongodb+srv://" in mongo_url:
    # MongoDB Atlas connection - add TLS options
    client = AsyncIOMotorClient(
        mongo_url,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        retryWrites=True,
        w="majority"
    )
else:
    # Local MongoDB connection
    client = AsyncIOMotorClient(mongo_url)

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