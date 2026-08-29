const API = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : '';

// ── Auth helpers ─────────────────────────────────────────────────────────────
function getToken()  { return localStorage.getItem('megeb_token'); }
function getUser()   { const u = localStorage.getItem('megeb_user'); return u ? JSON.parse(u) : null; }
function setAuth(token, user) {
  localStorage.setItem('megeb_token', token);
  localStorage.setItem('megeb_user', JSON.stringify(user));
}
function clearAuth() {
  localStorage.removeItem('megeb_token');
  localStorage.removeItem('megeb_user');
}
function isLoggedIn() { return !!getToken(); }

// ── Toast notification ────────────────────────────────────────────────────────
function showToast(msg, type = 'error') {
  let t = document.getElementById('megeb-toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'megeb-toast';
    t.style.cssText = `position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
      padding:12px 24px;border-radius:10px;font-family:Georgia,serif;font-size:15px;
      color:#fff;z-index:99999;opacity:0;transition:opacity .3s;max-width:420px;text-align:center;`;
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.background = type === 'error' ? '#c0392b' : '#263020';
  t.style.opacity = '1';
  clearTimeout(t._hide);
  t._hide = setTimeout(() => { t.style.opacity = '0'; }, 3500);
}

async function apiFetch(path, opts = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(API + path, { ...opts, headers });
  } catch (networkErr) {
    const msg = 'Cannot connect to server. Is the backend running?';
    showToast(msg);
    throw new Error(msg);
  }

  if (!res.ok) {
    let body = {};
    try { body = await res.json(); } catch (_) {}

    // Unified error shape: { error: true, message, code }
    if (body.error && body.message) {
      showToast(body.message);
      throw new Error(body.message);
    }

    // FastAPI validation errors: { detail: [...] }
    const detail = body.detail;
    const msg = Array.isArray(detail)
      ? detail.map(d => d.msg || String(d)).join(', ')
      : (typeof detail === 'string' ? detail : `Error ${res.status}`);
    showToast(msg);
    throw new Error(msg);
  }
  return res.json();
}

// ── Auth ─────────────────────────────────────────────────────────────────────
async function signup(name, email, password, nationality) {
  const data = await apiFetch('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ name, email, password, nationality })
  });
  setAuth(data.access_token, data.user);
  return data.user;
}

async function login(email, password) {
  const data = await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  });
  setAuth(data.access_token, data.user);
  return data.user;
}

// ── Recipes (legacy) ─────────────────────────────────────────────────────────
async function fetchTrending(limit = 8) {
  return apiFetch(`/recipes/trending?limit=${limit}`);
}

async function fetchRecipes(page = 1, limit = 12) {
  return apiFetch(`/recipes/?page=${page}&limit=${limit}`);
}

async function searchRecipes(q, page = 1, limit = 12) {
  return apiFetch(`/recipes/search/q?q=${encodeURIComponent(q)}&page=${page}&limit=${limit}`);
}

async function fetchRecipe(id) {
  return apiFetch(`/recipes/${id}`);
}

async function postRecipe(data) {
  return apiFetch('/recipes/', { method: 'POST', body: JSON.stringify(data) });
}

// ── Dishes ───────────────────────────────────────────────────────────────────
async function fetchDishes(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiFetch(`/api/dishes${qs ? '?' + qs : ''}`);
}

// Simple cache for dishes to improve performance
const dishesCache = new Map();
async function fetchDishesWithCache(params = {}) {
  const cacheKey = JSON.stringify(params);
  if (dishesCache.has(cacheKey)) {
    return dishesCache.get(cacheKey);
  }
  const result = await fetchDishes(params);
  dishesCache.set(cacheKey, result);
  // Clear cache after 5 minutes
  setTimeout(() => dishesCache.delete(cacheKey), 5 * 60 * 1000);
  return result;
}

async function fetchDish(slug) {
  return apiFetch(`/api/dishes/${slug}`);
}

async function submitDish(data) {
  return apiFetch('/api/dishes', { method: 'POST', body: JSON.stringify(data) });
}

async function fetchVariation(slug, variationId) {
  return apiFetch(`/api/dishes/${slug}/variations/${variationId}`);
}

async function submitVariation(slug, data) {
  return apiFetch(`/api/dishes/${slug}/variations`, { method: 'POST', body: JSON.stringify(data) });
}

// ── Moderation ────────────────────────────────────────────────────────────────
async function moderationQueue() {
  return apiFetch('/api/moderation/queue');
}

async function moderateDish(id, action) {
  return apiFetch(`/api/moderation/dishes/${id}`, { method: 'PATCH', body: JSON.stringify({ action }) });
}

async function moderateVariation(id, action) {
  return apiFetch(`/api/moderation/variations/${id}`, { method: 'PATCH', body: JSON.stringify({ action }) });
}

// ── Image Upload ──────────────────────────────────────────────────────────────
async function uploadImage(file) {
  const token = getToken();
  const form = new FormData();
  form.append('file', file);
  let res;
  try {
    res = await fetch(`${API}/api/upload/image`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: form,
    });
  } catch (_) {
    const msg = 'Cannot connect to server.';
    showToast(msg);
    throw new Error(msg);
  }
  if (!res.ok) {
    let body = {};
    try { body = await res.json(); } catch (_) {}
    const msg = (body.error && body.message) ? body.message : (body.detail || `Upload failed ${res.status}`);
    showToast(msg);
    throw new Error(msg);
  }
  return res.json(); // { url: "..." }
}

// ── Pantry ───────────────────────────────────────────────────────────────────
async function pantryList() {
  return apiFetch('/pantry/');
}

async function pantryAdd(item) {
  return apiFetch('/pantry/', { method: 'POST', body: JSON.stringify(item) });
}

async function pantryRemove(id) {
  return apiFetch(`/pantry/${id}`, { method: 'DELETE' });
}

// ── Meal Planner ──────────────────────────────────────────────────────────────
async function mealPlanGet(weekLabel) {
  return apiFetch(`/meal-plan/${encodeURIComponent(weekLabel)}`);
}

async function mealPlanSave(data) {
  return apiFetch('/meal-plan/', { method: 'POST', body: JSON.stringify(data) });
}

// ── Nutrition Log ─────────────────────────────────────────────────────────────
async function nutritionList(date = '') {
  const qs = date ? `?date=${encodeURIComponent(date)}` : '';
  return apiFetch(`/nutrition${qs}`);
}

async function nutritionLog(entry) {
  return apiFetch('/nutrition', { method: 'POST', body: JSON.stringify(entry) });
}

async function nutritionDelete(id) {
  return apiFetch(`/nutrition/${id}`, { method: 'DELETE' });
}

// ── AI ───────────────────────────────────────────────────────────────────────
async function aiChat(message) {
  return apiFetch('/ai/chat', { method: 'POST', body: JSON.stringify({ message }) });
}

async function aiImageRecipe(imageBase64) {
  return apiFetch('/ai/image-recipe', { method: 'POST', body: JSON.stringify({ image_base64: imageBase64 }) });
}

async function aiGenerate(params = {}) {
  return apiFetch('/ai/generate', { method: 'POST', body: JSON.stringify(params) });
}

// ── Nav state (call on every page) ───────────────────────────────────────────
function updateNav() {
  const user = getUser();
  const loginLink  = document.getElementById('nav-login');
  const logoutLink = document.getElementById('nav-logout');
  const addLink    = document.getElementById('nav-add');
  const userName   = document.getElementById('nav-username');
  const adminLink  = document.getElementById('nav-admin');

  if (user) {
    if (loginLink)  loginLink.style.display  = 'none';
    if (logoutLink) logoutLink.style.display = 'inline';
    if (addLink)    addLink.style.display    = 'inline';
    if (userName)   userName.textContent     = user.name.split(' ')[0];
    if (adminLink)  adminLink.style.display  = user.role === 'admin' ? 'inline' : 'none';
  } else {
    if (loginLink)  loginLink.style.display  = 'inline';
    if (logoutLink) logoutLink.style.display = 'none';
    if (addLink)    addLink.style.display    = 'none';
    if (userName)   userName.textContent     = '';
    if (adminLink)  adminLink.style.display  = 'none';
  }
}

function logout() {
  clearAuth();
  window.location.href = 'index.html';
}


// ── Collections ───────────────────────────────────────────────────────────────
async function fetchCollections() {
  return apiFetch('/api/collections');
}

async function fetchCollection(slug) {
  return apiFetch(`/api/collections/${slug}`);
}

// ── AI Substitute ─────────────────────────────────────────────────────────────
async function aiSubstitute(ingredient, dishContext = '') {
  return apiFetch('/ai/substitute', {
    method: 'POST',
    body: JSON.stringify({ ingredient, dish_context: dishContext }),
  });
}

// ── Contributors ──────────────────────────────────────────────────────────────
async function fetchTopContributors(limit = 10) {
  return apiFetch(`/api/contributors/top?limit=${limit}`);
}
