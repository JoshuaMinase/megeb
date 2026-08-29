import asyncio
import os
from dotenv import load_dotenv
from database import dishes

load_dotenv()

async def extract_unique_dishes():
    """Extract unique dishes from the database (by name) and save to a file"""
    print("Connecting to database and extracting unique dishes...")
    
    try:
        # Get all dishes from the database
        all_dishes = await dishes.find({}).to_list(length=None)
        print(f"Found {len(all_dishes)} total dishes in database")
        
        # Create a dictionary to track unique dishes by name
        unique_dishes = {}
        for dish in all_dishes:
            name = dish.get("name", "")
            if name and name not in unique_dishes:
                unique_dishes[name] = dish
        
        print(f"Found {len(unique_dishes)} unique dishes")
        
        # Convert to list and sort by name
        dish_list = list(unique_dishes.values())
        dish_list.sort(key=lambda x: x["name"].lower())
        
        # Format the data for the document
        formatted_dishes = []
        for dish in dish_list:
            dish_info = {
                "name": dish.get("name", ""),
                "name_amharic": dish.get("name_amharic", ""),
                "slug": dish.get("slug", ""),
                "category": dish.get("category", ""),
                "region": dish.get("region", ""),
                "description": dish.get("description", ""),
                "current_image_url": dish.get("reference_image_url", ""),
                "variation_count": dish.get("variation_count", 0),
                "status": dish.get("status", ""),
                "id": str(dish.get("_id", ""))
            }
            formatted_dishes.append(dish_info)
        
        # Create markdown document
        markdown_content = "# Megeb Dishes - Image Assignment\n\n"
        markdown_content += f"Total unique dishes: {len(formatted_dishes)}\n\n"
        markdown_content += "## Instructions\n"
        markdown_content += "1. Find appropriate images for each dish\n"
        markdown_content += "2. Update the `new_image_url` field with your image URL\n"
        markdown_content += "3. Save this file and I can create a script to update the database\n\n"
        markdown_content += "---\n\n"
        
        for i, dish in enumerate(formatted_dishes, 1):
            markdown_content += f"## {i}. {dish['name']}\n"
            if dish['name_amharic']:
                markdown_content += f"**Amharic:** {dish['name_amharic']}\n"
            markdown_content += f"**Slug:** {dish['slug']}\n"
            markdown_content += f"**Category:** {dish['category']}\n"
            if dish['region']:
                markdown_content += f"**Region:** {dish['region']}\n"
            markdown_content += f"**Description:** {dish['description']}\n"
            markdown_content += f"**Current Image URL:** {dish['current_image_url'] or 'No image'}\n"
            markdown_content += f"**Variations:** {dish['variation_count']}\n"
            markdown_content += f"**Status:** {dish['status']}\n"
            markdown_content += f"**Database ID:** {dish['id']}\n"
            markdown_content += f"**New Image URL:** [ENTER YOUR IMAGE URL HERE]\n"
            markdown_content += "\n---\n\n"
        
        # Save to file
        output_file = "unique_dishes_for_images.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"Successfully extracted {len(formatted_dishes)} unique dishes to {output_file}")
        print("You can now manually add image URLs to this file.")
        
        return formatted_dishes
        
    except Exception as e:
        print(f"Error extracting dishes: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(extract_unique_dishes())