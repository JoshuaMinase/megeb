import asyncio
import os
from dotenv import load_dotenv
from database import dishes

load_dotenv()

async def get_all_dishes():
    """Get ALL dishes from the database"""
    print("Connecting to database and getting ALL dishes...")
    
    try:
        # Get all dishes from the database without any filtering
        all_dishes = await dishes.find({}).to_list(length=None)
        print(f"Total dishes found: {len(all_dishes)}")
        
        # Print all dish names
        print("\n=== ALL DISH NAMES ===")
        for i, dish in enumerate(all_dishes, 1):
            name = dish.get("name", "Unknown")
            slug = dish.get("slug", "no-slug")
            status = dish.get("status", "unknown")
            print(f"{i}. {name} (slug: {slug}, status: {status})")
        
        # Also check if there are any other collections that might contain dishes
        from database import db as megeb_db
        collections = await megeb_db.list_collection_names()
        print(f"\n=== ALL COLLECTIONS IN DATABASE ===")
        for collection in collections:
            count = await megeb_db[collection].count_documents({})
            print(f"{collection}: {count} documents")
        
        return all_dishes
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(get_all_dishes())