<div align="center">

# 🍽️ Megeb - Ethiopian Recipe Platform

*A modern, community-driven recipe platform featuring authentic Ethiopian cuisine powered by AI*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)](https://www.mongodb.com/atlas)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Image%20Storage-blue?logo=cloudinary)](https://cloudinary.com)

</div>

## ✨ Features

- **🍴 Extensive Recipe Database** - 79+ authentic Ethiopian dishes with real cookbook photography
- **🤖 AI-Powered Search** - Intelligent recipe discovery using RAG (Retrieval-Augmented Generation) with Groq
- **👥 Community Contributions** - User-submitted recipes with moderation system
- **🌍 Personalized Experience** - Nationality-based recommendations and trending dishes
- **📸 Rich Media** - High-quality images hosted on Cloudinary
- **🔐 Secure Authentication** - JWT-based auth with role-based access control
- **📊 Meal Planning** - Integrated pantry management and nutrition tracking
- **🔄 Recipe Variations** - Multiple recipe variations per dish with rating system

## 🏗️ Architecture

### Tech Stack

- **Frontend**: Plain HTML/CSS/JavaScript (no build step required)
- **Backend**: FastAPI with Motor (async MongoDB driver)
- **Database**: MongoDB Atlas (production) or local MongoDB (development)
- **Image Storage**: Cloudinary CDN
- **AI**: Groq API for intelligent recipe generation and search
- **Authentication**: JWT with bcrypt password hashing

### System Design

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   MongoDB       │
│  (Static HTML)  │◄──►│   (FastAPI)     │◄──►│    Atlas        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │  Cloudinary  │
                       │   Images     │
                       └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB Atlas account (free tier available)
- Cloudinary account (free tier available)
- Groq API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/megeb.git
   cd megeb
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Seed the database with Ethiopian recipes**
   ```bash
   python seed_gursha.py
   ```

5. **Index recipes for AI search**
   ```bash
   python rag_index.py
   ```

6. **Start the backend server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Serve the frontend**
   ```bash
   # In a new terminal
   cd frontend
   python -m http.server 3000
   ```

8. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
megeb/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── seed_gursha.py          # Ethiopian recipes seeder
│   ├── rag_index.py            # AI search indexing
│   ├── requirements.txt        # Python dependencies
│   ├── models/                 # Pydantic models
│   ├── routes/                 # API route handlers
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── dish_routes.py      # Dish/recipe endpoints
│   │   ├── ai_routes.py        # AI-powered endpoints
│   │   └── ...
│   └── ...
├── frontend/
│   ├── foods.html              # Main recipe feed
│   ├── login.html              # Authentication pages
│   ├── signup.html
│   ├── js/                     # Frontend JavaScript
│   │   ├── config.js           # API configuration
│   │   ├── auth.js             # Authentication logic
│   │   └── ...
│   └── css/                    # Styling
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── README.md                   # This file
└── render.yaml                 # Render deployment config
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/megeb` |
| `DB_NAME` | Database name | `megeb` |
| `JWT_SECRET` | Secret key for JWT token generation | `your-super-secret-key` |
| `GROQ_API_KEY` | Groq API key for AI features | `gsk_...` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | `your-cloud-name` |
| `CLOUDINARY_API_KEY` | Cloudinary API key | `123456789` |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | `your-secret` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,https://yourdomain.com` |

## 🌐 Deployment

### Render Deployment (Recommended)

The project includes `render.yaml` for easy deployment to Render:

1. **Push your code to GitHub**
2. **Create a new web service on Render**
3. **Connect your GitHub repository**
4. **Render will auto-detect the Python service**
5. **Set environment variables in Render dashboard**
6. **Deploy!**

### Manual Deployment

#### Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend

The frontend is static and can be served by any web server:

**Nginx example:**
```nginx
server {
    listen 80;
    root /path/to/megeb/frontend;
    index index.html;

    location /api/ {
        proxy_pass http://localhost:8000;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 🤖 AI Features

### RAG-Powered Search

The platform uses Retrieval-Augmented Generation for intelligent recipe search:

- **3,277 indexed chunks** from the Gursha cookbook
- **Context-aware responses** grounded in authentic recipes
- **3 AI endpoints**: Chat, Generate, and Fix Recipe

### AI Endpoints

- `POST /ai/chat` - Conversational recipe assistance
- `POST /ai/generate` - Generate new recipes from descriptions
- `POST /ai/fix` - Fix and improve existing recipes

## 📊 Database Schema

### Collections

- **users** - User accounts with authentication and preferences
- **dishes** - Main recipe dishes with metadata and images
- **recipe_variations** - Multiple recipe variations per dish
- **rag_chunks** - Indexed text chunks for AI search
- **pantry_items** - User pantry management
- **meal_plans** - User meal planning

## 🔐 Authentication & Authorization

### User Roles

- **user** - Standard user access
- **admin** - Full administrative privileges

### Admin Setup

Promote a user to admin directly in MongoDB:

```javascript
db.users.updateOne(
  { email: "admin@example.com" },
  { $set: { role: "admin" } }
)
```

## 🧪 Testing

### API Testing

The FastAPI auto-generated documentation at `/docs` provides interactive API testing.

### Manual Testing

1. **Test user registration**: `POST /auth/signup`
2. **Test login**: `POST /auth/login`
3. **Test recipe feed**: `GET /api/dishes`
4. **Test AI search**: `POST /ai/chat`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Gursha Cookbook** - Authentic Ethiopian recipes from "Gursha: Timeless Recipes for Modern Kitchens"
- **Ethiopian Community** - Cultural insights and recipe validation
- **Open Source Community** - Tools and libraries that make this project possible

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

<div align="center">

**Built with ❤️ for the Ethiopian food community**

[⭐ Star this repo](https://github.com/yourusername/megeb) • [🐛 Report issues](https://github.com/yourusername/megeb/issues) • [📖 Documentation](https://github.com/yourusername/megeb/wiki)

</div>
