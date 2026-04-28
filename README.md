# 📡 SourceRadar

**A personalized project discovery tool for developers.**

SourceRadar aggregates trending content from GitHub, Hacker News, and Product Hunt, then filters and ranks it based on your personal interest tags — so you only see what actually matters to you.

![Login Page](https://github.com/user-attachments/assets/86d8be52-61ee-4313-8e5d-823075a185fa)

## ✨ Features

- **🔐 User Auth** — Register, login, JWT-based sessions (7-day tokens)
- **🏷️ Interest Tags** — Pick from 20 predefined tags (AI, Rust, Python, React, DevOps, Indie Dev…) or add custom ones
- **📰 Personalized Feed** — Content scored and ranked by how well it matches your tags; filter by source (All / GitHub / Hacker News / Product Hunt)
- **🔍 Search** — Full-text search across all aggregated content
- **📬 Weekly Email Reports** — Auto-generated top-picks sent every Monday; manually triggerable from the UI
- **⏱️ Scheduled Scraping** — Runs every 6 hours automatically; manual refresh also available

## 🗂️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy, SQLite |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Scraping | httpx, BeautifulSoup4, APScheduler |
| Email | aiosmtplib (SMTP) |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Deployment | Docker, Docker Compose, nginx |

## 🚀 Quick Start

### Option 1 — Docker Compose (recommended)

```bash
git clone https://github.com/typing233/SourceRadar
cd SourceRadar
cp backend/.env.example backend/.env   # edit as needed
docker-compose up --build
```

Open **http://localhost** in your browser.

### Option 2 — Local Development

**Backend:**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit as needed
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev                   # starts on http://localhost:3000
```

## ⚙️ Configuration

Copy `backend/.env.example` to `backend/.env` and configure:

```env
SECRET_KEY=change-me-in-production

# Optional: SMTP for email reports
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your@gmail.com

FRONTEND_URL=http://localhost:3000
```

If `SMTP_USER` / `SMTP_PASSWORD` are not set, weekly reports are printed to the server log instead of emailed.

## 📸 Screenshots

### Feed — Personalized Discovery
![Feed](https://github.com/user-attachments/assets/fb399f47-3f29-47d8-b1a6-80cc858ee742)

### Profile — Interest Tags & Notifications
![Profile](https://github.com/user-attachments/assets/5d8db2ea-b247-4e45-8955-67701cc8d7af)

### Weekly Report
![Weekly Report](https://github.com/user-attachments/assets/17f24c94-3074-4836-bcf4-23b9ff74250b)

## 🗄️ API Reference

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login → returns JWT |
| GET  | `/api/auth/me` | Get current user |
| GET  | `/api/content/feed` | Personalized feed (paginated, filterable by source) |
| GET  | `/api/content/search?q=` | Full-text search |
| POST | `/api/content/refresh` | Trigger manual scrape |
| GET  | `/api/users/profile` | Get user profile |
| PUT  | `/api/users/tags` | Update interest tags |
| PUT  | `/api/users/profile` | Update profile settings |
| GET  | `/api/reports/weekly` | Get this week's top picks |
| POST | `/api/reports/send` | Send weekly report email |

Interactive Swagger docs at **http://localhost:8000/docs**.

## 📁 Project Structure

```
SourceRadar/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + startup lifespan
│   │   ├── config.py         # Settings via pydantic-settings
│   │   ├── database.py       # SQLAlchemy + SQLite
│   │   ├── models/           # User, Content ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── routers/          # auth, content, users, reports
│   │   ├── scrapers/         # GitHub Trending, Hacker News, Product Hunt
│   │   └── services/         # Recommendation engine, email, scheduler
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Layout, ContentCard, TagSelector, LoadingSpinner
│   │   ├── pages/            # Login, Register, Feed, Profile, WeeklyReport
│   │   ├── services/api.ts   # Axios API client with auth interceptors
│   │   └── context/          # AuthContext (React Context + JWT)
│   ├── package.json
│   ├── vite.config.ts        # Dev proxy: /api → localhost:8000
│   └── Dockerfile
└── docker-compose.yml
```
