import asyncio
import os
from dotenv import load_dotenv
from database import dishes, recipes, recipe_variations

load_dotenv()

async def get_complete_food_list():
    """Get complete food information from all collections"""
    print("Getting complete food list from database...")
    
    try:
        # Get all dishes
        all_dishes = await dishes.find({}).to_list(length=None)
        print(f"Total dishes: {len(all_dishes)}")
        
        # Get all recipes
        all_recipes = await recipes.find({}).to_list(length=None)
        print(f"Total recipes: {len(all_recipes)}")
        
        # Get all recipe variations
        all_variations = await recipe_variations.find({}).to_list(length=None)
        print(f"Total recipe variations: {len(all_variations)}")
        
        # Create a comprehensive list
        food_items = {}
        
        # Add dishes
        for dish in all_dishes:
            name = dish.get("name", "")
            if name:
                if name not in food_items:
                    food_items[name] = {
                        "name": name,
                        "name_amharic": dish.get("name_amharic", ""),
                        "slug": dish.get("slug", ""),
                        "category": dish.get("category", ""),
                        "region": dish.get("region", ""),
                        "description": dish.get("description", ""),
                        "current_image_url": dish.get("reference_image_url", ""),
                        "variations": dish.get("variation_count", 0),
                        "status": dish.get("status", ""),
                        "source": "dishes"
                    }
        
        # Add recipes (might have additional info)
        for recipe in all_recipes:
            name = recipe.get("name", "")
            if name and name in food_items:
                # Update with recipe info if available
                if not food_items[name]["description"]:
                    food_items[name]["description"] = recipe.get("description", "")
                if not food_items[name]["current_image_url"]:
                    food_items[name]["current_image_url"] = recipe.get("image_url", "")
                food_items[name]["nationality"] = recipe.get("nationality", "")
                food_items[name]["ingredients"] = recipe.get("ingredients", [])
                food_items[name]["steps"] = recipe.get("steps", [])
        
        # Convert to sorted list
        food_list = sorted(food_items.values(), key=lambda x: x["name"].lower())
        
        print(f"\nTotal unique food items: {len(food_list)}")
        
        # Create comprehensive markdown document
        markdown_content = "# Complete Megeb Food List\n\n"
        markdown_content += f"Total unique food items: {len(food_list)}\n"
        markdown_content += f"Total database entries: {len(all_dishes)} dishes + {len(all_recipes)} recipes + {len(all_variations)} variations\n\n"
        markdown_content += "## Instructions\n"
        markdown_content += "1. Find appropriate images for each food item\n"
        markdown_content += "2. Update the `new_image_url` field with your image URL\n"
        markdown_content += "3. Save this file and I can create a script to update the database\n\n"
        markdown_content += "---\n\n"
        
        for i, food in enumerate(food_list, 1):
            markdown_content += f"## {i}. {food['name']}\n"
            if food.get('name_amharic'):
                markdown_content += f"**Amharic:** {food['name_amharic']}\n"
            markdown_content += f"**Slug:** {food['slug']}\n"
            markdown_content += f"**Category:** {food['category']}\n"
            if food.get('region'):
                markdown_content += f"**Region:** {food['region']}\n"
            if food.get('nationality'):
                markdown_content += f"**Nationality:** {food['nationality']}\n"
            markdown_content += f"**Description:** {food['description']}\n"
            markdown_content += f"**Current Image URL:** {food['current_image_url'] or 'No image'}\n"
            markdown_content += f"**Variations:** {food['variations']}\n"
            markdown_content += f"**Status:** {food['status']}\n"
            if food.get('ingredients'):
                markdown_content += f"**Ingredients:** {', '.join(food['ingredients'][:5])}...\n"
            markdown_content += f"**New Image URL:** [ENTER YOUR IMAGE URL HERE]\n"
            markdown_content += "\n---\n\n"
        
        # Save to file
        output_file = "complete_food_list.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"Successfully created {output_file} with {len(food_list)} unique food items")
        
        return food_list
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(get_complete_food_list())