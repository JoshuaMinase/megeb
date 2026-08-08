import asyncio
from database import dishes, recipe_variations

async def check():
    dish_count = await dishes.count_documents({})
    var_count = await recipe_variations.count_documents({})
    
    print(f"Total dishes: {dish_count}")
    print(f"Total variations: {var_count}")
    
    # Check a sample dish
    doro = await dishes.find_one({"name": "Doro Wat"})
    if doro:
        print(f"Doro Wat found: {doro.get('name')}")
        print(f"Doro Wat image: {doro.get('reference_image_url', 'not found')}")
        print(f"Doro Wat youtube_url: {doro.get('youtube_url', 'not found')}")
    
    # Check a sample variation
    doro_var = await recipe_variations.find_one({"variation_name": "Classic Doro Wat"})
    if doro_var:
        print(f"Classic Doro Wat variation found")
        print(f"Variation YouTube URL: {doro_var.get('youtube_url', 'not found')}")

asyncio.run(check())