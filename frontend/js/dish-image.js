// Dish image handling utilities

// Default images mapping for common Ethiopian dishes.
// Order matters: getDishImageSrc/dishImageFallbackByName test these as
// substrings against the dish name in insertion order, so more specific
// keys (e.g. 'tibs') are listed before broader catch-alls (e.g. 'doro',
// 'wot') to stop dishes like "Doro Tibs" being caught by the wrong key.
const DISH_IMAGE_MAP = {
  'kitfo': 'images/food-kitfo.jpg',
  'shiro': 'images/food-shiro.jpg',
  'tibs': 'images/food-tibs.jpg',
  'fir-fir': 'images/food-injera.jpg',
  'fit-fit': 'images/food-injera.jpg',
  'injera': 'images/food-injera.jpg',
  'taita': 'images/food-injera.jpg',
  'doro': 'images/food-doro.jpg',
  'wot': 'images/food-doro.jpg',
  'wat': 'images/food-doro.jpg',
};

// Default fallback images by category. Only categories where a real photo
// is genuinely representative are listed here - everything else (snack,
// side, salad, condiment, etc.) falls through to DEFAULT_IMAGE rather than
// being forced into a photo that doesn't actually match.
const CATEGORY_IMAGE_MAP = {
  'main': 'images/food-doro.jpg',
  'bread': 'images/food-injera.jpg',
  'breakfast': 'images/food-injera.jpg',
};

// Generic fallback image
const DEFAULT_IMAGE = 'images/food-doro.jpg';

/**
 * Get the image source URL for a dish
 * @param {Object} dish - Dish object. Dishes from the API use
 *   `reference_image_url`; recipe variations use `image_url`. Both are
 *   checked so real photos (e.g. from the Wikipedia image-fix job) are
 *   actually used instead of silently falling through to the local
 *   placeholder images below.
 * @returns {string} Image URL
 */
function getDishImageSrc(dish) {
  if (!dish) return DEFAULT_IMAGE;

  // First try a real photo on the dish/variation itself
  const realPhoto = dish.image_url || dish.reference_image_url;
  if (realPhoto && realPhoto.trim() !== '') {
    return realPhoto;
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