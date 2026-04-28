# SourceRadar

> A personalized project discovery tool for developers — aggregates GitHub Trending, Hacker News, and Product Hunt into a scored, tag-filtered feed.

## Features

- **Personalized Feed** — Items scored by overlap with your interest tags (AI, Rust, frontend, etc.)
- **Multi-source aggregation** — GitHub Trending, Hacker News (score > 50), Product Hunt daily
- **Weekly Digest** — Auto-generated & emailed every Monday 08:00 UTC
- **JWT Authentication** — Secure login / registration
- **Scheduled crawls** — Every 6 hours via APScheduler

## Quick Start (Docker Compose)

```bash
cp backend/.env.example backend/.env
# Edit backend/.env to set SECRET_KEY and optionally SMTP settings
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

All settings via `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `DATABASE_URL` | `sqlite:///./data/sourceradar.db` | SQLAlchemy DB URL |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS) |
| `SMTP_USER` | `` | SMTP username / email |
| `SMTP_PASSWORD` | `` | SMTP password / app password |
| `SMTP_FROM` | `SourceRadar <noreply@sourceradar.dev>` | From address |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user info |
| GET | `/api/items` | Personalized feed (paginated) |
| GET | `/api/user/tags` | Get interest tags |
| PUT | `/api/user/tags` | Update interest tags |
| PUT | `/api/user/settings` | Update digest preference |
| GET | `/api/digest` | Latest digest |
| POST | `/api/digest/generate` | Generate & email digest now |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy (SQLite), APScheduler, python-jose, passlib, httpx, BeautifulSoup4, aiosmtplib, Jinja2
- **Frontend**: React 18, Vite, react-router-dom, axios
- **Infrastructure**: Docker Compose, nginx
