# Megeb — Ethiopian Recipe Platform

A people's recipe platform where anyone can share food and ingredients.
Features: dish feed with variation system, nationality-based recommendations, trending, search, auth, pantry, nutrition log, meal planner, AI recipe generation.

---

## Stack

- **Frontend** — plain HTML/CSS/JS (no build step)
- **Backend** — FastAPI + Motor (async MongoDB)
- **Database** — MongoDB (local or Atlas)

---

## Run Locally

### 1. Install MongoDB

https://www.mongodb.com/try/download/community — runs on port 27017 by default.

### 2. Install Python dependencies

```
cd backend
pip install fastapi uvicorn motor "python-jose[cryptography]" "passlib[bcrypt]" python-multipart python-dotenv Pillow bleach slowapi
```

### 3. Configure environment

```
cp backend/.env.example backend/.env
```

Edit `backend/.env` — fill in:
- `GROQ_API_KEY` — from https://console.groq.com
- `JWT_SECRET` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `MONGO_URL` — default `mongodb://localhost:27017`

### 4. Seed the database (first time only)

```
cd backend
python seed_data.py
```

To migrate existing flat recipes into the dishes/variations model:

```
cd backend
python migrate_to_dishes.py
```

### 5. Start the API server

```
cd backend
uvicorn main:app --reload --port 8000
```

API: **http://localhost:8000** · Docs: **http://localhost:8000/docs**

### 6. Open the frontend

Open `index.html` in your browser, or visit http://localhost:8000

---

## API Endpoints

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/signup | — | Register: name, email, password, nationality |
| POST | /auth/login | — | Login, returns JWT |

### Recipes (legacy flat model)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /recipes/ | optional | Paginated list, personalised if logged in |
| POST | /recipes/ | required | Add a recipe |
| GET | /recipes/trending | — | Top recipes by search count |
| GET | /recipes/{id} | — | Single recipe |
| GET | /recipes/search/q?q= | optional | Full-text search |

### Dishes & Variations (new model)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/dishes | — | List approved dishes; ?category=, ?search=, ?page=, ?limit= |
| POST | /api/dishes | required | Submit a new dish (status: pending) |
| GET | /api/dishes/{slug} | — | Dish detail + approved variations |
| GET | /api/dishes/{slug}/variations/{id} | — | Single variation detail |
| POST | /api/dishes/{slug}/variations | required | Submit a variation (status: pending) |

### Moderation (admin only)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/moderation/queue | admin | All pending dishes + variations |
| PATCH | /api/moderation/dishes/{id} | admin | Approve or reject a dish — body: `{"action":"approve"\|"reject"}` |
| PATCH | /api/moderation/variations/{id} | admin | Approve or reject a variation — body: `{"action":"approve"\|"reject"}` |

### Upload

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/upload/image | required | Upload image (jpg/png/webp, ≤5MB); returns { url } |

### Pantry

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /pantry/ | required | List pantry items |
| POST | /pantry/ | required | Add item: name, quantity, unit, expiry |
| DELETE | /pantry/{id} | required | Remove item |

### Nutrition Log

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /nutrition | required | List logs; ?date=YYYY-MM-DD |
| POST | /nutrition | required | Log a meal: recipe_name, calories, protein, carbs, fat, date |
| DELETE | /nutrition/{id} | required | Delete a log entry |

### Meal Planner

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /meal-plan/{week_label} | required | Get week plan |
| POST | /meal-plan/ | required | Save week plan: week_label, days dict |

### AI (Groq — rate limited)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /ai/chat | — | Chat with Ethiopian cooking assistant |
| POST | /ai/generate | — | Generate recipe from ingredients/constraints |
| POST | /ai/image-recipe | — | Image-to-recipe (vision stub) |

---

## Data Model

### dishes collection
```json
{
  "slug": "firfir",
  "name": "Firfir",
  "name_amharic": "ፍርፍር",
  "category": "breakfast",
  "region": "optional",
  "description": "short canonical description",
  "reference_image_url": "/uploads/firfir-ref.jpg",
  "status": "approved | pending | rejected",
  "submitted_by": "user_id or null",
  "variation_count": 0,
  "search_count": 0,
  "created_at": "ISO date"
}
```

### recipe_variations collection
```json
{
  "dish_id": "ref to dishes._id",
  "variation_name": "Classic",
  "author_id": "user_id",
  "ingredients": [],
  "steps": [],
  "image_url": "...",
  "prep_time_minutes": 10,
  "cook_time_minutes": 15,
  "servings": 2,
  "spice_level": "mild | medium | spicy",
  "notes": "what makes this version different",
  "status": "approved | pending | rejected",
  "likes_count": 0,
  "search_count": 0,
  "created_at": "ISO date"
}
```

---

## Folder Structure

```
recipy/
├── index.html          Homepage
├── foods.html          Dish feed (trending + paginated + search)
├── recipe.html         Dish detail + variation switcher
├── add-recipe.html     Submit dish or variation (requires login)
├── admin.html          Moderation queue (admin only)
├── signup.html / login.html
├── pantry.html
├── css/style.css
├── js/
│   ├── api.js          API client + auth helpers
│   └── main.js         Scroll effects, sticky header, animations
├── images/
└── backend/
    ├── main.py
    ├── database.py
    ├── auth.py
    ├── seed_data.py
    ├── migrate_to_dishes.py
    ├── models/schemas.py
    ├── routes/
    │   ├── auth_routes.py
    │   ├── recipe_routes.py
    │   ├── dish_routes.py
    │   ├── moderation_routes.py
    │   ├── upload_routes.py
    │   ├── ai_routes.py
    │   ├── pantry_routes.py
    │   ├── nutrition_routes.py
    │   └── meal_plan_routes.py
    └── uploads/        Uploaded images (git-ignored)
```

---

## How personalisation works

1. User signs up → chooses nationality
2. `GET /recipes/` checks JWT → gets user nationality
3. MongoDB aggregation scores matching-nationality recipes higher
4. `GET /api/dishes` returns approved dishes sorted by variation count + recency

## Moderation flow

1. User submits dish or variation → `status: "pending"`
2. Admin sees it in `/api/moderation/queue`
3. Admin approves → `status: "approved"`, appears in feed
4. Dish `variation_count` is incremented when a variation is approved

## Admin setup

Promote a user to admin directly in MongoDB:

```
db.users.updateOne({ email: "your@email.com" }, { $set: { role: "admin" } })
```
