# 📡 SourceRadar

A personalized project discovery tool for developers. Automatically scrapes GitHub Trending, Hacker News, and Product Hunt, then delivers a curated feed based on your interest tags.

## Features

- 🔍 Scrapes GitHub Trending, Hacker News, and Product Hunt every 6 hours
- 🎯 Personalized feed based on your interest tags
- 📧 Weekly email reports every Monday
- 🔐 JWT-based authentication

## Quick Start

### Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

- `SECRET_KEY` - JWT secret key
- `SMTP_*` - Email settings (optional, falls back to console logging)

## API

- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `GET /api/content/feed` - Personalized feed
- `GET /api/content/search?q=...` - Search
- `PUT /api/users/tags` - Update tags
- `GET /api/reports/weekly` - Weekly report