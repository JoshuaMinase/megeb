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

## Render Deployment

📄 **Detailed deployment guide available in [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

### Quick Deploy to Render

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Create Render account**
   - Go to [render.com](https://render.com) and sign up
   - Connect your GitHub repository

3. **Deploy using render.yaml**
   - Render will automatically detect the `render.yaml` file
   - It will create two services: `megeb-backend` and `megeb-frontend`
   - The backend will be deployed as a Python web service
   - The frontend will be deployed as a static site

4. **Configure Environment Variables**
   In your Render dashboard, set these environment variables for the backend service:
   
   Required:
   - `MONGO_URL`: Your MongoDB Atlas connection string
   - `GROQ_API_KEY`: Your Groq API key for AI features
   - `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
   - `CLOUDINARY_API_KEY`: Your Cloudinary API key
   - `CLOUDINARY_API_SECRET`: Your Cloudinary API secret
   
   Auto-generated:
   - `JWT_SECRET`: Render will auto-generate this
   
   Pre-configured:
   - `CORS_ORIGINS`: Set to your Render URLs
   - `PORT`: Set to 8000

5. **Access your application**
   - Frontend: `https://megeb-frontend.onrender.com`
   - Backend API: `https://megeb-backend.onrender.com`

### Manual Render Setup (Alternative)

If you prefer to set up Render manually without `render.yaml`:

**Backend Service:**
- Type: Web Service
- Environment: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Working Directory: `backend`

**Frontend Service:**
- Type: Static Site
- Build Command: `echo "No build required"`
- Publish Directory: `frontend`

### Post-Deployment Setup

1. **Update CORS Origins**
   - After deployment, update the `CORS_ORIGINS` environment variable
   - Include both your frontend and backend Render URLs

2. **Set up Admin User**
   - Connect to MongoDB Atlas
   - Promote a user to admin:
   ```javascript
   db.users.updateOne({ email: "your@email.com" }, { $set: { role: "admin" } })
   ```

3. **Custom Domain (Optional)**
   - Add custom domains in Render dashboard
   - Update CORS origins to include your custom domain
   - Update `frontend/js/config.js` if needed

### Render-Specific Considerations

- **Free Tier**: Render's free tier has spin-up time (services sleep when inactive)
- **Environment Variables**: Must be set in Render dashboard, not in `.env` file
- **Database**: Use MongoDB Atlas for best performance with Render
- **File Storage**: Use Cloudinary for image uploads (Render has ephemeral filesystem)
- **Logging**: Check Render dashboard for logs and monitoring
