# Megeb — Ethiopian Recipe Platform

A people's recipe platform where anyone can share food and ingredients.
Features: dish feed with variation system, nationality-based recommendations, trending, search, auth, pantry, nutrition log, meal planner, AI recipe generation.

---

## Stack

- **Frontend** — plain HTML/CSS/JS (no build step)
- **Backend** — FastAPI + Motor (async MongoDB)
- **Database** — MongoDB Atlas (production) or local MongoDB (development)
- **Image Storage** — Cloudinary
- **AI** — Groq API

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

---

## Deployment

### Quick Start with Docker Compose

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd megeb
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values:
   # - MONGO_URL: Your MongoDB Atlas connection string
   # - JWT_SECRET: generate a secure random string
   # - GROQ_API_KEY: get from https://console.groq.com/
   # - CLOUDINARY_*: get from https://cloudinary.com/
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Manual Deployment

#### Backend

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0"
   export JWT_SECRET="your-secret-key"
   export GROQ_API_KEY="your-groq-key"
   export CLOUDINARY_CLOUD_NAME="your-cloud-name"
   export CLOUDINARY_API_KEY="your-api-key"
   export CLOUDINARY_API_SECRET="your-api-secret"
   export CORS_ORIGINS="http://localhost:3000"
   ```

3. **Run the backend**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

#### Frontend

The frontend is static HTML/CSS/JS. Serve it with any web server:

**Using nginx:**
```nginx
server {
    listen 80;
    root /path/to/frontend;
    index index.html;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**Using Python:**
```bash
cd frontend
python -m http.server 3000
```

### Production Considerations

- Use MongoDB Atlas for production database
- Set strong JWT_SECRET and rotate it regularly
- Enable HTTPS/TLS
- Configure proper CORS origins for your domain
- Use a production WSGI server like Gunicorn with Uvicorn workers
- Set up proper logging and monitoring
- Configure Cloudinary for production image storage

---

## Hybrid Deployment (Recommended)

### Architecture
- **Frontend**: Vercel (static site with global CDN)
- **Backend**: Render (Python FastAPI web service)
- **Database**: MongoDB Atlas (shared between both)

### Quick Deploy

#### 1. Deploy Backend to Render
📄 **Detailed guide: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

```bash
# Push to GitHub
git add .
git commit -m "Add deployment configuration"
git push origin main

# Deploy to Render using render.yaml
# Backend will be deployed as Python web service
```

**Backend URL**: `https://megeb-backend.onrender.com`

#### 2. Deploy Frontend to Vercel
📄 **Detailed guide: [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)**

```bash
# Import repository in Vercel
# Vercel will auto-detect vercel.json
# Frontend will be deployed as static site
```

**Frontend URL**: `https://your-app.vercel.app`

#### 3. Configure CORS
After both deployments, update backend CORS origins:
```
https://megeb-backend.onrender.com,https://your-vercel-app.vercel.app
```

### Benefits of Hybrid Deployment
- ✅ **Performance**: Vercel's global CDN for static assets
- ✅ **Cost**: Both platforms have generous free tiers
- ✅ **Scalability**: Scale frontend and backend independently
- ✅ **Reliability**: Redundant deployment across platforms
- ✅ **Developer Experience**: Excellent DX on both platforms

---

## Alternative: All-in-One Render Deployment

📄 **Detailed guide: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

If you prefer to deploy both frontend and backend on Render:

1. **Deploy using render.yaml**
   - Render will create both services
   - Frontend: Static site
   - Backend: Python web service

2. **Access your application**
   - Frontend: `https://megeb-frontend.onrender.com`
   - Backend: `https://megeb-backend.onrender.com`

### Render-Specific Considerations

- **Free Tier**: Render's free tier has spin-up time (services sleep when inactive)
- **Environment Variables**: Must be set in Render dashboard
- **Database**: Use MongoDB Atlas for best performance
- **File Storage**: Use Cloudinary for image uploads
- **Logging**: Check Render dashboard for logs

---

## Environment Configuration

### Required Environment Variables

For both deployment methods, configure these in your platform's dashboard:

**Database:**
- `MONGO_URL`: MongoDB Atlas connection string

**Authentication:**
- `JWT_SECRET`: Auto-generated by Render (set manually for other platforms)

**AI Features:**
- `GROQ_API_KEY`: Your Groq API key for AI recipe generation

**Image Storage:**
- `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
- `CLOUDINARY_API_KEY`: Your Cloudinary API key
- `CLOUDINARY_API_SECRET`: Your Cloudinary API secret

**CORS:**
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### Environment-Specific Notes

**Local Development:**
- Use `.env` file (not committed to git)
- See `.env.example` for template

**Render:**
- Set in Render dashboard
- Auto-generated for JWT_SECRET
- Manual entry for other variables

**Vercel:**
- Frontend doesn't require environment variables
- Backend (on Render) handles all environment config
