# InterviewIQ AI Backend — Integration Status

## Canonical architecture

All backend modules now run from the single root `app/` package and share:

- one FastAPI application
- one JWT authentication system
- one `users` / `roles` identity model
- one database URL
- one SQLAlchemy metadata registry
- one Alembic migration chain

The synchronous resume/optimizer services use a small sync SQLAlchemy session pointed at the **same** `DATABASE_URL` as the canonical async application session. This keeps their existing service implementations usable while they are being migrated to async incrementally.

## Integrated modules

- Core authentication, users and roles
- Interview engine
- Coding engine
- Feedback and roadmap
- Resume upload and PDF parsing
- AI resume analysis
- Company matching
- Resume optimization
- Interview readiness prediction
- Recruiter endpoints
- Notifications

## Important runtime requirements

1. Copy `.env.example` to `.env`.
2. Set `SECRET_KEY`.
3. Set `DATABASE_URL` to PostgreSQL using `postgresql+asyncpg://...`.
4. Install `requirements.txt`.
5. Run `alembic upgrade head`.
6. Start with `uvicorn app.main:app --reload`.

Resume uploads use local storage by default. Gemini features require `GEMINI_API_KEY`.

## API groups

All routes are under `/api/v1`.

Examples:

- `/api/v1/auth/...`
- `/api/v1/resumes/...`
- `/api/v1/resumes/{resume_id}/analyze`
- `/api/v1/resumes/{resume_id}/company-match`
- `/api/v1/resumes/{resume_id}/optimize`
- `/api/v1/readiness/analyze`
- `/api/v1/recruiter/...`
- `/api/v1/notifications/...`

## Verification performed

- Python compilation of the integrated `app/` package: passed.
- SQLAlchemy model registry import: passed.
- 38 ORM tables are registered in the single metadata registry.
- New migration `0004_resume_ai_and_career_modules.py` was added after `0003`.

A full live API/database test still requires installing the pinned dependencies and providing a reachable PostgreSQL instance.
