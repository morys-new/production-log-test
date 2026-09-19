# ProdLog — Nawasentra's Junior Software Engineer Hiring Coding Test Repo

A pre-wired scaffold for a 90-minute live coding test. The product requirements are **not** in
this repository — they are in your invitation email (a copy is in [`TASK.md`](TASK.md) once
your session begins).

Your job is to design the schema, API, and data shapes. This repo removes environment friction
and shows the layering conventions you are expected to follow.

## 10-minute quickstart

### 1. Prerequisites

- Python 3.10+, Node 20+, git, and either Docker or a local Postgres 13+ installation.
- Run the doctor first (stdlib only, safe to run before installing anything):

```bash
python scripts/doctor.py
```

### 2. Start Postgres

**Option A — Docker (recommended)**

```bash
docker compose up -d db
```

**Option B — local Postgres**

```bash
# bash
createdb production_log_test

# PowerShell
createdb production_log_test
```

### 3. Backend

```bash
# bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit DATABASE_URL if your credentials differ
python scripts/apply_migration.py
uvicorn main:app --reload

# PowerShell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1    # if blocked: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
pip install -r requirements.txt
cp .env.example .env
python scripts/apply_migration.py
uvicorn main:app --reload
```

Visit <http://localhost:8000/health> — you should see `{"status":"ok","db_version":"..."}`.

### 4. Web

```bash
# bash / PowerShell
cd web
cp .env.example .env
npm ci
npm run dev
```

Visit <http://localhost:3000>.

### 5. Mobile

```bash
# bash / PowerShell
cd mobile
cp .env.example .env     # adjust EXPO_PUBLIC_API_BASE_URL for your device (see below)
npm ci
npx expo start --web     # web is the minimum; emulator/device are optional
```

## Repo map

```
production-log-test/
  README.md                     you are here
  TASK.md                       task specification (populated at session start)
  docker-compose.yml            Postgres 16 on port $POSTGRES_PORT (default 5432)
  scripts/doctor.py             stdlib-only environment checker
  shared/types.ts               shared TypeScript types (import type only, never redefined)
  backend/
    main.py                     FastAPI app entry point
    config.py                   pydantic-settings: DATABASE_URL, CORS_ORIGINS
    errors.py                   ApiError + exception handler (error envelope)
    db/                         raw asyncpg helpers (no ORM)
    models/                     Pydantic response models
    routers/                    thin route handlers
    services/                   intentionally empty
    migration.sql               your DDL goes here
    scripts/apply_migration.py  applies migration.sql in one transaction
    requirements.txt            pinned runtime deps
    requirements-dev.txt        adds ruff, mypy, stubs
    pyproject.toml              ruff + mypy config (target py310)
  web/                          Next.js app (App Router) — see web/README when added
  mobile/                       Expo app — see mobile/README when added
```

## Non-negotiable conventions

These apply to everything you add. Violating them is a red flag.

| Rule |
|---|
| FastAPI + raw asyncpg — **no ORM** |
| `response_model=` on **every** endpoint |
| Thin routers — logic lives in `services/` or `db/` |
| Full type hints on every function (`mypy --strict` must pass; TS `strict: true`, no `any`) |
| API types live in `shared/types.ts` — **imported, never redefined** in web or mobile |
| Always `import type` for shared types |

---

## The health endpoint — follow this pattern

```
GET /health  →  200 {"status": "ok", "db_version": "PostgreSQL 16.x ..."}
              →  503 {"error": {"code": "DB_UNAVAILABLE", "message": "..."}}
```

**Layering — read the existing health files and apply the same structure to your work:**

```
routers/health.py
    db/health.py
    models/health.py
errors.py
```

## Command reference

| Action | Command |
|---|---|
| Environment check | `python scripts/doctor.py` |
| Apply migration | `cd backend && python scripts/apply_migration.py` |
| Reset DB schema | `cd backend && python scripts/apply_migration.py --reset --yes` |
| Start backend | `cd backend && uvicorn main:app --reload` |
| Backend lint | `cd backend && ruff check .` |
| Backend types | `cd backend && mypy --strict .` |
| Start web | `cd web && npm run dev` |
| Web lint | `cd web && npm run lint` |
| Web types | `cd web && npm run type-check` |
| Start mobile (web) | `cd mobile && npx expo start --web` |
| Mobile types | `cd mobile && npm run type-check` |

## Mobile networking notes

- **Android emulator:** use `http://10.0.2.2:8000` (maps to host `localhost`).
- **iOS simulator:** use `http://localhost:8000`.
- **Physical device:** use your computer's LAN IP, e.g. `http://192.168.1.x:8000`.

Set `EXPO_PUBLIC_API_BASE_URL` in `mobile/.env` accordingly.

At minimum, verify the mobile app compiles and renders with `npx expo start --web`.
Emulator/device testing is optional for this exercise.
Expo Go on your device must match the SDK version declared in `mobile/app.json`.

## Troubleshooting

**Port already in use**
```bash
# find the PID and kill it, or change the port:
uvicorn main:app --reload --port 8001
```

**Postgres auth / role error**
Your local Postgres may require a different user. Edit `DATABASE_URL` in `backend/.env`:
```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/production_log_test
```
Make sure the role has `CREATE TABLE` privileges on the database.

**`gen_random_uuid()` not found**
This function is built-in from Postgres 13. If you see this error, upgrade your Postgres server.

**CORS error in browser**
The backend reads `CORS_ORIGINS` from `backend/.env`. Add your frontend origin:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**PowerShell: `.venv\Scripts\Activate.ps1` blocked**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Wrong Node version**
Use nvm: `nvm install 20 && nvm use 20`. Or download directly from https://nodejs.org.

**`docker compose` not found**
On older Docker installs it is `docker-compose` (with a hyphen). Either upgrade Docker Desktop
or alias it: `alias docker compose='docker-compose'`.

## Fair game

- Adding dependencies is fine — add them to the appropriate requirements / package.json and
  explain your choice.
- Do not restructure the existing directory layout; the paths above are referenced in the
  invitation email.
- You may add your own agent-instruction files (CLAUDE.md, .cursorrules, etc.).
