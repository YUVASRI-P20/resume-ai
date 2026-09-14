# InterviewIQ AI — Backend (Module 1 & 2)

Production-ready FastAPI foundation + authentication/user management for
InterviewIQ AI. Built with Clean Architecture, SOLID principles, the
Repository pattern, a Service layer, and dependency injection throughout.

## Quick start

```bash
cp .env.example .env               # then edit SECRET_KEY, DATABASE_URL, etc.
docker compose up --build          # postgres + redis + api, migrations run automatically
# API docs: http://localhost:8000/api/v1/docs
```

Local (non-Docker) dev:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Run tests (uses in-memory SQLite, no external services needed):

```bash
pytest -v --cov=app
```

Create the first admin account (ADMIN is never created via `/register`):

```bash
python -m scripts.seed_admin admin@interviewiq.ai "S3curePass1" "Platform Admin"
```

## 1. Architecture

Layered / Clean Architecture with a strict dependency direction —
outer layers depend on inner layers, never the reverse:

```
Router (api/v1/endpoints)      <- HTTP only: parse request, call service, return response
    v
Service (services)             <- business rules, orchestration, transactions
    v
Repository (repositories)      <- data access only, one per aggregate/model
    v
Model (models)                 <- SQLAlchemy ORM entities
```

- **Repository Pattern** — every model gets a repository exposing
  query methods (`get_by_email`, `revoke_all_for_user`, ...). Nothing
  outside `repositories/` writes raw SQLAlchemy queries.
- **Service Layer** — `AuthService`, `UserService` own every business
  rule (password strength is schema-level, but "can this email
  register", "rotate this refresh token", "burn all sessions on
  password reset" all live here). Services raise typed domain
  exceptions (`app/core/exceptions.py`), never `HTTPException`.
- **Dependency Injection** — FastAPI's `Depends()` wires a DB session
  into a repository into a service into a router at request time
  (`api/deps.py`). Nothing is a global singleton except stateless
  utilities (settings, the rate limiter).
- **SOLID** — e.g. `BaseRepository[ModelType]` (generic, open for
  extension), `AppException` subclasses (each owns its own status
  code — routers/handlers don't need `if/elif` chains), swappable
  `EmailService` (single responsibility, easy to replace with a real
  provider).

## 2. Folder structure

```
app/
  api/
    deps.py                  # get_db, get_current_user, get_current_active_user
    v1/
      router.py               # aggregates all v1 routers
      endpoints/
        health.py
        auth.py
        users.py
  core/
    config.py                 # pydantic-settings, reads .env
    logging.py                # structured logging + request-id injection
    exceptions.py             # domain exception hierarchy
  database/
    session.py                 # async engine + get_db dependency
    base.py                    # DeclarativeBase + UUID/timestamp mixins
  models/                      # SQLAlchemy ORM: Role, User, RefreshToken
  schemas/                     # Pydantic v2 request/response models
  repositories/                # data access, one file per model
  services/                    # business logic: AuthService, UserService, EmailService
  middleware/                  # RequestIDMiddleware, AccessLogMiddleware, exception handlers
  security/                    # password hashing, JWT, RBAC (require_roles)
  utils/                       # rate_limiter
  main.py                      # app factory
alembic/                       # migrations (0001 creates roles/users/refresh_tokens + seeds roles)
scripts/seed_admin.py          # bootstrap the first ADMIN
tests/                         # pytest + httpx, SQLite in-memory
```

## 3. Database design

```
roles                          users                          refresh_tokens
--------------                 --------------------------     -----------------------------
id (uuid, pk)                  id (uuid, pk)                  id (uuid, pk)
name (unique)                  email (unique, indexed)        user_id (fk -> users.id, cascade)
description                    hashed_password                 token_hash (unique, indexed)  <- SHA-256, never the raw JWT
created_at / updated_at        full_name                       expires_at
                                role_id (fk -> roles.id)        revoked (bool)
                                is_active                       replaced_by_token_hash
                                is_email_verified               user_agent / ip_address
                                created_at / updated_at         created_at / updated_at
```

- UUID primary keys everywhere (`sqlalchemy.Uuid`, dialect-agnostic —
  native `uuid` type on Postgres, works on SQLite for tests too).
- `roles` is a real table (not a bare enum column) seeded with
  `STUDENT` / `RECRUITER` / `ADMIN` in migration `0001`, so it stays
  introspectable and extensible without a schema change later.
- Refresh tokens are stored **hashed**, with `revoked` +
  `replaced_by_token_hash` for full rotation auditing — a DB leak
  never hands out a usable token, and reuse of a rotated-out token is
  detectable (see auth flow below).
- Every table has `created_at` / `updated_at`, indexes on FK and
  lookup columns (`email`, `token_hash`, `role_id`, `user_id`).

## 4. Authentication flow

- **Register** (`POST /auth/register`) — STUDENT or RECRUITER only
  (ADMIN is provisioned via `scripts/seed_admin.py`, never publicly).
  Hashes the password (Argon2id, bcrypt fallback for old hashes),
  creates the user, sends a verification email, and returns an
  access/refresh pair immediately — no separate login step required.
- **Login** (`POST /auth/login`) — verifies credentials, issues a new
  access/refresh pair.
- **Access tokens** — short-lived JWT (default 15 min), `Bearer` in
  `Authorization` header, carries `sub` (user id) and `role`.
- **Refresh tokens** — longer-lived (default 7 days), persisted
  **hashed** in `refresh_tokens`. `POST /auth/refresh` rotates: the
  old token is marked `revoked` + `replaced_by_token_hash`, a new pair
  is issued. If a **revoked** token is presented again (theft/replay
  signal), every refresh token for that user is immediately revoked.
- **Logout** (`POST /auth/logout`) — revokes the given refresh token.
  Idempotent — logging out twice is not an error.
- **Forgot / reset password** — `forgot-password` always returns the
  same message whether or not the email exists (no user enumeration);
  the emailed token is single-purpose (`type=password_reset`) and
  short-lived. Resetting a password revokes every existing session.
- **Email verification** — single-purpose, 24h token, sets
  `is_email_verified`. Login does not currently block on this (it's a
  soft gate future modules can enforce, e.g. before starting an
  interview) — flip that in `AuthService.login` if a hard gate is
  wanted.
- **RBAC** — `require_roles(RoleName.ADMIN, ...)` (`security/permissions.py`)
  is a drop-in `Depends()` any future router can use.

## 5. API endpoints

| Method | Path                          | Auth        | Description                              |
|--------|-------------------------------|-------------|-------------------------------------------|
| GET    | `/api/v1/health`              | none        | Liveness check                           |
| POST   | `/api/v1/auth/register`       | none        | Register (STUDENT/RECRUITER)             |
| POST   | `/api/v1/auth/login`          | none        | Login                                    |
| POST   | `/api/v1/auth/logout`         | none        | Revoke a refresh token                   |
| POST   | `/api/v1/auth/refresh`        | none        | Rotate access/refresh pair               |
| POST   | `/api/v1/auth/forgot-password`| none        | Send password reset email                |
| POST   | `/api/v1/auth/reset-password` | none        | Reset password via token                 |
| POST   | `/api/v1/auth/verify-email`   | none        | Verify email via token                   |
| GET    | `/api/v1/auth/me`             | Bearer      | Current user                             |
| GET    | `/api/v1/users/me`            | Bearer      | Current user's profile                   |
| PATCH  | `/api/v1/users/me`            | Bearer      | Update profile (full_name)               |
| GET    | `/api/v1/users/admin/ping`    | Bearer, ADMIN | Reference RBAC-gated route              |

Full interactive docs: `/api/v1/docs` (Swagger) and `/api/v1/redoc`.

## 6. How future modules should integrate

1. **Add your model(s)** under `app/models/`, import them in
   `app/models/__init__.py` (so Alembic autogenerate picks them up),
   and generate a migration: `alembic revision --autogenerate -m "add resume tables"`.
2. **Add a repository** in `app/repositories/` extending `BaseRepository[YourModel]`.
3. **Add a service** in `app/services/` — inject the repositories it
   needs, raise `app.core.exceptions` subclasses for error cases
   (they're automatically translated into proper HTTP responses —
   nothing to do in the router).
4. **Add an endpoints module** under `app/api/v1/endpoints/`, protect
   routes with `Depends(get_current_active_user)` and, where a
   specific role is required, `Depends(require_roles(RoleName.X))`.
   Register the router in `app/api/v1/router.py`.
5. **Reuse, don't duplicate**: `get_db`, `get_current_user`,
   `get_current_active_user`, `require_roles`, the JWT/password
   utilities, the exception hierarchy, and the response envelopes in
   `schemas/common.py` are all designed to be imported as-is by every
   future module (resume analyzer, interview engine, coding engine,
   recruiter dashboard, etc.) — none of it is auth-module-specific.
6. **Background work** (resume parsing, AI feedback generation) should
   go through Celery — `REDIS_URL` / `CELERY_BROKER_URL` are already
   configured; add task modules under a new `app/tasks/` package and a
   `celery_app.py` when that module starts.

## Security checklist (implemented)

- [x] Argon2id password hashing (bcrypt fallback)
- [x] JWT access + refresh, `type`-claimed to prevent cross-use
- [x] Refresh-token rotation with reuse/theft detection
- [x] Refresh tokens stored hashed, never raw
- [x] Role-based authorization (`STUDENT` / `RECRUITER` / `ADMIN`)
- [x] Public registration cannot self-assign `ADMIN`
- [x] No user-enumeration on forgot-password
- [x] Password-reset revokes all existing sessions
- [x] Rate limiting on auth endpoints (slowapi)
- [x] CORS restricted to configured origins
- [x] Input validation (Pydantic v2) incl. password strength rules
- [x] SQL injection prevention (parameterized queries via SQLAlchemy ORM)
- [x] Structured error responses, no stack traces leaked to clients
- [x] Request-ID correlation for log tracing
- [x] Secrets only via environment variables (`.env`, never committed)
