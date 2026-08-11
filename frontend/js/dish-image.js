// Dish image handling utilities

// Default images mapping for common Ethiopian dishes
const DISH_IMAGE_MAP = {
  'doro': 'images/food-doro.jpg',
  'doro wat': 'images/food-doro.jpg',
  'tibs': 'images/food-tibs.jpg',
  'firfir': 'images/food-firfir.jpg',
  'shiro': 'images/food-shiro.jpg',
  'injera': 'images/food-photo-1.png',
  'kitfo': 'images/food-doro.jpg',
  'wot': 'images/food-doro.jpg',
};

// Default fallback images by category
const CATEGORY_IMAGE_MAP = {
  'main': 'images/food-doro.jpg',
  'breakfast': 'images/food-photo-1.png',
  'snack': 'images/food-tibs.jpg',
  'salad': 'images/food-firfir.jpg',
  'condiment': 'images/food-shiro.jpg',
};

// Generic fallback image
const DEFAULT_IMAGE = 'images/food-doro.jpg';

/**
 * Get the image source URL for a dish
 * @param {Object} dish - Dish object with image_url, name, category properties
 * @returns {string} Image URL
 */
function getDishImageSrc(dish) {
  // First try the dish's image_url if available
  if (dish.image_url && dish.image_url.trim() !== '') {
    return dish.image_url;
  }
  
  // Try to match by dish name (case-insensitive)
  if (dish.name) {
    const nameLower = dish.name.toLowerCase();
    for (const [key, value] of Object.entries(DISH_IMAGE_MAP)) {
      if (nameLower.includes(key)) {
        return value;
      }
    }
  }
  
  // Try to match by category
  if (dish.category && CATEGORY_IMAGE_MAP[dish.category]) {
    return CATEGORY_IMAGE_MAP[dish.category];
  }
  
  // Fall back to default
  return DEFAULT_IMAGE;
}

/**
 * Fallback handler when dish image fails to load
 * @param {HTMLImageElement} img - The image element that failed to load
 * @param {string} name - Dish name
 * @param {string} category - Dish category
 */
function dishImageFallbackByName(img, name, category) {
  // Prevent infinite loops
  if (img.dataset.fallbackAttempted) {
    return;
  }
  img.dataset.fallbackAttempted = 'true';
  
  // Try to find a fallback image based on name
  if (name) {
    const nameLower = name.toLowerCase();
    for (const [key, value] of Object.entries(DISH_IMAGE_MAP)) {
      if (nameLower.includes(key) && img.src !== value) {
        img.src = value;
        return;
      }
    }
  }
  
  // Try category fallback
  if (category && CATEGORY_IMAGE_MAP[category] && img.src !== CATEGORY_IMAGE_MAP[category]) {
    img.src = CATEGORY_IMAGE_MAP[category];
    return;
  }
  
  // Final fallback to default
  if (img.src !== DEFAULT_IMAGE) {
    img.src = DEFAULT_IMAGE;
  }
}