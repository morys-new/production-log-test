# ProdLog — Nawasentra's Junior Software Engineer Hiring Coding Test Repo

A pre-wired scaffold for a live coding test. The product requirements are in
[`TASK.md`](TASK.md).

Your job is to design the schema, API, and data shapes. This repo removes environment friction
and shows the layering conventions you are expected to follow.

## Get your own copy

You do this live, at the start of the session — it's part of your 15 minutes of setup time.

1. Open this repo on GitHub and click **"Use this template" → "Create a new repository"**.
   Set it to **Private**.
2. In your new repo: **Settings → Collaborators**, add the interviewer's GitHub username.
3. Share your repo URL in the call.
4. Clone your new repo and continue with the quickstart below.

Use the setup time only to get your environment running — clone, configure `.env` files,
install dependencies, confirm the app starts. Don't design the schema or write endpoint code
yet; that starts when the coding timer does.

## 15-minute quickstart

### 1. Prerequisites

- Python 3.10+, git, and either Docker or a local Postgres 13+ installation.
- Node 20.19.4+ (or 22.13+, 24.3+) and npm. The mobile toolchain (React Native 0.86) rejects
  older Node 20/22 releases. `nvm install 20` picks a compatible version.
- Run the doctor first (stdlib only, safe to run before installing anything). Expect a few
  FAILs until setup is done; run it again at the end with the backend venv activated:

```bash
python scripts/doctor.py
```

### 2. Start Postgres

**Option A — Docker (recommended)**

```bash
docker compose up -d prodlog-db
```

**Option B — local Postgres**

```bash
createdb production_log_test
```

Then set `DATABASE_URL` in `backend/.env` (created in step 3) to your own user, password and
port. The Docker setup here uses port 5434 (not Postgres's default 5432) specifically so it
doesn't collide with a Postgres you may already have installed locally. A local install
typically uses 5432 by default — set that port in `DATABASE_URL` instead if you're using your
own local Postgres.

### 3. Backend

```bash
# bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # edit DATABASE_URL if your credentials differ
python scripts/apply_migration.py
uvicorn main:app --reload

# PowerShell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1    # if blocked: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
pip install -r requirements-dev.txt
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
  TASK.md                       the task specification
  docker-compose.yml            Postgres 16 on host port $POSTGRES_PORT (default 5434)
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
    requirements-dev.txt        runtime deps plus ruff, mypy, stubs
    pyproject.toml              ruff + mypy config (target py310)
  web/                          Next.js app (App Router)
  mobile/                       Expo app (expo-router)
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
| Web build | `cd web && npm run build` |
| Start mobile (web) | `cd mobile && npx expo start --web` |
| Mobile lint | `cd mobile && npm run lint` |
| Mobile types | `cd mobile && npm run type-check` |

## Mobile networking notes

- **Android emulator:** use `http://10.0.2.2:8000` (maps to host `localhost`).
- **iOS simulator:** use `http://localhost:8000`.
- **Physical device:** use your computer's LAN IP, e.g. `http://192.168.1.x:8000`.

Set `EXPO_PUBLIC_API_BASE_URL` in `mobile/.env` accordingly.

At minimum, verify the mobile app compiles and renders with `npx expo start --web`.
Emulator/device testing is optional for this exercise.
Expo Go on your device must support the Expo SDK in `mobile/package.json` (SDK 57).

## Troubleshooting

**Port already in use**
```bash
# find the PID and kill it, or change the port:
uvicorn main:app --reload --port 8001
```
If you move the backend, update `NEXT_PUBLIC_API_BASE_URL` in `web/.env` and
`EXPO_PUBLIC_API_BASE_URL` in `mobile/.env` to match.

**Postgres port already taken, or auth fails against the wrong server**
Another Postgres on the same port answers first, with different credentials. Pick a free port:
```bash
# bash
POSTGRES_PORT=5435 docker compose up -d prodlog-db
# PowerShell
$env:POSTGRES_PORT = "5435"; docker compose up -d prodlog-db
```
and use the same port in `DATABASE_URL` in `backend/.env`.

**Backend exits at startup with "Cannot connect to Postgres"**
Postgres is not running or `DATABASE_URL` points at the wrong host or port.
Start it (`docker compose up -d prodlog-db`) and check `backend/.env`.

**Postgres auth / role error**
Your local Postgres may require a different user. Edit `DATABASE_URL` in `backend/.env`:
```
DATABASE_URL=postgresql://<user>:<password>@localhost:<port>/production_log_test
```
Make sure the role has `CREATE TABLE` privileges on the database.

**`gen_random_uuid()` not found**
This function is built-in from Postgres 13. If you see this error, upgrade your Postgres server.

**CORS error in browser**
The backend reads `CORS_ORIGINS` from `backend/.env`. Add your frontend origin:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8081
```

**PowerShell: `.venv\Scripts\Activate.ps1` blocked**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Wrong Node version**
Use nvm: `nvm install 20 && nvm use 20`. Or download directly from https://nodejs.org.

**`docker compose` not found**
Older Docker installs ship it as `docker-compose` (with a hyphen). Use that spelling, or
upgrade Docker Desktop.

## Fair game

- Adding dependencies is fine — add them to the appropriate requirements / package.json and
  explain your choice.
- Do not restructure the existing directory layout; the paths above are referenced in the
  invitation email.
- You may add your own agent-instruction files (CLAUDE.md, .cursorrules, etc.).
