# Car Scraper

Full-stack web application for scraping and managing car listings.

## Tech Stack

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: Next.js (Pages Router) + TypeScript
- API base route: `http://localhost:8000/api`
- Frontend URL: `http://localhost:3000`

## Project Structure

- `backend/` - FastAPI API, scraping service, DB models, routes
- `frontend/` - legacy CRA React app (old)
- `frontend/` - new Next.js + TypeScript app (active migration target)

## Prerequisites

- Python 3.10+ (recommended 3.11)
- Node.js 18+ and npm
- PostgreSQL (local or hosted)

## 1) Backend Setup

From project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Backend Environment Variables

Create or update `backend/.env` with your values:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<database>
SECRET_KEY=<your-strong-random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional mail settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<your-email>
SMTP_PASSWORD=<your-app-password>
SMTP_FROM=<from-email>
```

### Run Backend

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Quick API check:

- Open `http://localhost:8000/api/`
- Expected response includes: `"status": "running"`

## 2) Frontend Setup (Next.js + TypeScript)

From project root:

```powershell
cd frontend
npm install
```

### Frontend Environment Variables

Create or update `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Run Frontend

```powershell
cd frontend
npm run dev
```

Then open:

- `http://localhost:3000`

## 3) Run Full Project (Two Terminals)

Terminal 1 (backend):

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (frontend):

```powershell
cd frontend
npm run dev
```

## Useful Commands

Backend dependencies:

```powershell
cd backend
pip install -r requirements.txt
```

Frontend production build:

```powershell
cd frontend
npm run build
```

Frontend lint:

```powershell
cd frontend
npm run lint
```

## Troubleshooting

- If frontend cannot call API, verify `NEXT_PUBLIC_BACKEND_URL` in `frontend/.env.local`.
- If backend fails to start, verify `DATABASE_URL` and PostgreSQL access.
- If CORS issues occur, check allowed origins in `backend/main.py`.
- If `uvicorn` is not found, activate the backend virtual environment first.
