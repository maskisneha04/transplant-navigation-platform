# AI-Enabled Transplant Navigation and Coordination Platform

> Academic/research capstone prototype. This is a **coordination and administrative-support system** — it does not diagnose, determine transplant eligibility, allocate organs, or match donors to recipients. All centre/patient data used for development is **synthetic** and clearly labelled as such.

## Status: Phase 2 complete (patient case management + professional UI)

### What works right now
**Phase 1 (unchanged, regression-tested):** registration, login, JWT auth, RBAC, protected routes, audit logging.

**Phase 2 (new):**
- Full transplant case lifecycle: `POST/GET/PATCH /cases`, `/cases/{id}`, `/cases/{id}/status`, `/cases/{id}/timeline`
- Controlled 7-state case status machine (NEW → DOCUMENT_COLLECTION → UNDER_REVIEW → COORDINATOR_REVIEW → CENTRE_REVIEW → COMPLETED, +CANCELLED), transitions centralized in `app/services/case_service.py`
- Server-side ownership enforcement — a patient can never view/edit another patient's case, even by guessing the URL ID (returns 404, not 403, to avoid confirming the case exists)
- Real, database-backed case timeline (no fabricated history)
- A reusable frontend component library (Button, Card, Input, Select, StatusBadge, EmptyState, ErrorState, Skeleton, Toast, ConfirmDialog, PageHeader, Breadcrumbs, AppShell) used consistently across every page
- New pages: `/cases`, `/cases/new`, `/cases/:id`; Login/Register/Dashboard visually upgraded
- 30 automated backend tests (10 Phase 1 + 20 Phase 2), all passing

### What's scaffolding only (built out in later phases)
Coordinator dashboard, AI centre recommendations, document intelligence, real-time updates, notifications, analytics — database tables exist, no working API/UI yet.

## Running locally (Docker — recommended)

```powershell
copy .env.example .env
docker compose up --build
```

```powershell
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_roles.py
docker compose exec backend python scripts/create_admin.py
```

- Backend API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Demo accounts
- `admin.demo@example.com` / `ChangeMe123!` — system_admin, created by `scripts/create_admin.py`
- Register your own patient account via the `/register` page

## Running backend tests

```powershell
docker compose exec postgres psql -U postgres -c "CREATE DATABASE transplant_test_db;"
docker compose exec backend pytest tests/ -v
```
Expected: `30 passed`.

## Environment variables
See `.env.example` — copy to `.env` and fill in a real `JWT_SECRET_KEY` for anything beyond local development. Never commit `.env`.

## Troubleshooting
- **`could not translate host name "postgres"`**: you're running the backend natively (not in Docker) — change `DATABASE_URL` in `backend/.env` to use `localhost` instead of `postgres`.
- **Postgres connection refused**: the Postgres container/service isn't running yet — `docker compose up -d postgres` or start your native PostgreSQL service.
- **`psql` not recognized**: not on PATH — either add `C:\Program Files\PostgreSQL\<version>\bin` to your PATH, or skip `psql` and use pgAdmin / the Python scripts instead, which don't need it.

## Project structure
See `docs/architecture-plan.md` for the full annotated structure and the 15-phase roadmap.

