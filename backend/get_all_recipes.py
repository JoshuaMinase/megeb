import asyncio
import os
from dotenv import load_dotenv
from database import recipes

load_dotenv()

async def get_all_recipes():
    """Get ALL recipes from the database"""
    print("Getting ALL recipes from database...")
    
    try:
        # Get all recipes from the database
        all_recipes = await recipes.find({}).to_list(length=None)
        print(f"Total recipes found: {len(all_recipes)}")
        
        # Print all recipe names
        print("\n=== ALL RECIPE NAMES ===")
        for i, recipe in enumerate(all_recipes, 1):
            name = recipe.get("name", "Unknown")
            nationality = recipe.get("nationality", "Unknown")
            print(f"{i}. {name} (nationality: {nationality})")
        
        return all_recipes
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(get_all_recipes())