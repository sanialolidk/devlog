# DevLog

A developer activity tracker — log coding sessions, tag them, and visualize your output over time.

**[Live Demo](https://devlog-zeta-ten.vercel.app)** · **[API Docs](https://devlog-api-production-b984.up.railway.app/docs)**

---

## Features

- Start and stop coding sessions with a description
- Tag sessions by project, language, or topic
- Dashboard with stats and a 7-day activity chart
- User accounts with JWT authentication
- CLI tool for logging sessions from the terminal
- REST API with interactive Swagger docs

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL |
| Auth | JWT tokens, bcrypt password hashing |
| Infra | Docker, Railway (API + DB), Vercel (frontend), GitHub Actions (CI) |
| CLI | Click, Rich |

## Running locally

**API**
```bash
git clone https://github.com/sanialolidk/devlog
cd devlog
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # add your DATABASE_URL and SECRET_KEY
alembic upgrade head
uvicorn devlog.api.main:app --reload --port 8001
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**CLI**
```bash
devlog start "working on auth"
devlog stop
devlog list
```

## API

Interactive docs available at `/docs`. Core endpoints:

```
POST   /auth/register
POST   /auth/login
GET    /sessions
POST   /sessions
PATCH  /sessions/{id}/stop
POST   /sessions/{id}/tags
GET    /tags
```
