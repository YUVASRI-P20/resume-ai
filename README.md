# 🧠 InterviewIQ AI — An Platform that helps you to prepare for Interview

> Production-ready AI Technical Interview Preparation and Career Readiness Platform.

---

## 🏗️ Architecture & Unified Directory Layout

```
INTERVIEWIQ/
├── backend/                       # FastAPI Clean Architecture Core & AI Services
│   ├── alembic/                   # Database migrations & schemas
│   ├── app/
│   │   ├── api/                   # REST API Routers (v1) & Dependency Injection
│   │   ├── core/                  # Configuration, Logging, Exceptions
│   │   ├── database/              # Async & Sync SQLAlchemy sessions
│   │   ├── middleware/            # Access logs, Request IDs, Error handlers
│   │   ├── models/                # SQLAlchemy ORM entities (Users, Roles, Interviews)
│   │   ├── repositories/          # Data Access Object (DAO) pattern
│   │   ├── resume/                # Resume Parser, Extractor & AI Claim Auditor
│   │   ├── schemas/               # Pydantic v2 schemas
│   │   ├── security/              # JWT tokens, RBAC, Password hashing
│   │   └── services/              # Business logic (AI Optimizer, Readiness, Coding)
│   ├── tests/                     # Pytest suite with in-memory SQLite
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── frontend/                      # Next.js 16.3 + React 19 + TypeScript + Tailwind
│   ├── public/                    # Static assets & icons
│   ├── src/
│   │   ├── app/                   # App Router pages (Dashboard, Interviews, Replays)
│   │   ├── components/            # UI Design system, Readiness cards, Radar charts
│   │   ├── constants/             # Default configurations and company benchmarks
│   │   ├── services/              # Axios API client & endpoints
│   │   ├── store/                 # Zustand state stores (Resume, Auth, Interview)
│   │   ├── types/                 # TypeScript interfaces
│   │   └── utils/                 # Utilities
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml             # Orchestration for Postgres, Redis, Backend, Frontend
├── start-all.bat                  # 1-Click Windows Batch startup
├── start-all.ps1                  # 1-Click PowerShell startup
└── README.md
```

---

## ⚡ Quick Start

### Option 1: One-Click Windows Startup (Local)
Double-click `start-all.bat` or run:
```powershell
.\start-all.ps1
```

### Option 2: Docker Compose (Full Stack)
```bash
docker compose up --build
```
* **Frontend**: [http://localhost:3000](http://localhost:3000)
* **Backend API**: [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger Docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### Option 3: Manual Startup

**1. Start Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or: .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📄 Dynamic Resume Parser & Claim Verification

The platform supports uploading any technical resume format (PDF, DOCX, TXT):
1. **Skill Extraction Engine**: Automatically extracts languages, frameworks, databases, and architectural tools.
2. **Resume Claim Auditor**: Detects and highlights technical claims (e.g. distributed caching, async concurrency) for targeted deep-dive questions.
3. **Role & ATS Match Scoring**: Predicts suitability for Top Tech benchmark profiles (Google, Vercel, Microsoft, Amazon, Zoho).
4. **Adaptive Mock Interviews**: Dynamically customizes interview questions to match the candidate's exact uploaded resume stack.
