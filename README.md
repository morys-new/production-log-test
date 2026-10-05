# ProdLog — Nawasentra's Junior Software Engineer Hiring Coding Test Repo

A pre-wired scaffold for a live coding test. The product requirements are in
[`TASK.md`](TASK.md).

Your job is to design the schema, API, and data shapes. This repo removes environment friction
and shows the layering conventions you are expected to follow.

## Implementation notes

What I built on the scaffold, and the decisions behind it. The spec leaves these open, so each
assumption below is a choice that can be revisited.

### API

| Endpoint | Purpose |
|---|---|
| `GET /pits`, `POST /pits` | List pits, create a pit (names are unique, ignoring case) |
| `GET /entries?status=&pit_id=` | List entries, newest report date first; both filters optional |
| `POST /entries` | Log an entry; it always starts as `draft` |
| `GET /entries/{id}` | One entry |
| `PATCH /entries/{id}` | Correct `planned_tonnes` / `actual_tonnes` while not approved |
| `PATCH /entries/{id}/status` | Move an entry through the workflow |
| `GET /summary?date_from=&date_to=` | Manager summary (see below) |

Every error uses the `{"error": {"code", "message"}}` envelope, request validation included
(`VALIDATION_ERROR`, 422). Other codes: `PIT_NAME_TAKEN` (409), `PIT_NOT_FOUND` (422),
`DUPLICATE_ENTRY` (409), `REPORT_DATE_IN_FUTURE` (422), `ENTRY_NOT_FOUND` (404),
`ENTRY_LOCKED` (409), `INVALID_STATUS_TRANSITION` (409), `INVALID_DATE_RANGE` (422).

### Workflow and the approved lock

- Allowed transitions: draft → submitted, submitted → approved, submitted → draft (sent back).
  Any other move is `INVALID_STATUS_TRANSITION`; any change to an approved entry is
  `ENTRY_LOCKED`.
- The service layer enforces this with one guarded `UPDATE … WHERE status …` statement, so the
  check and the write cannot be split by a concurrent request.
- A database trigger also rejects any UPDATE or DELETE of an approved row, as a safety net for
  clients that bypass the API.

### Summary: what a mine manager sees

- Planned vs actual tonnes, variance and achievement %, kept separate for ore and overburden:
  one combined number would hide whether the mine is producing ore or only moving waste.
- Stripping ratio (overburden tonnes per ore tonne), planned and actual, the main cost driver of
  an open-pit mine.
- Entry counts per status, showing how much of the picture is still provisional.
- The same figures per pit, including pits with no entries yet (shown as zeros), to spot which
  pit is behind or has not reported.
- An optional inclusive date range; all dates by default.

### Assumptions

1. There is one mine ("Test Mine A"), so there is no mines table.
2. Shifts are `day` and `night` (two 12-hour shifts); the spec does not name them.
3. A pit has at most one entry per report date, shift and material. A second one would
   double-count tonnes in the summary, so it is rejected with 409.
4. Tonnes are non-negative with at most 2 decimals (`NUMERIC(12,2)`); extra precision is
   rejected rather than rounded. A plan of 0 is allowed and gives a null achievement %.
5. A report date cannot be in the future (by the server's local date).
6. Only the numbers can be corrected, as the spec says. Pit, date, shift and material are fixed
   once logged.
7. There is no authentication or role model: the spec names operators and supervisors but no
   login, so anyone can submit, approve or send back. With auth, approving and sending back
   would be supervisor-only.
8. Summary totals include draft and submitted entries, to give a live picture; the status counts
   show how much is not final yet. Approved-only totals would be a one-line filter.
9. Web and mobile filter the loaded list on the client ("without re-fetching"). The API also
   supports server-side `?status=&pit_id=` filtering.
10. There is no pagination, which suits the size of this exercise.
11. The web page creates entries but does not change their status; the spec only asks for
    creation there. Status changes work through the API (`/docs`).

### Notes

- `migration.sql` is re-runnable: it drops and recreates the tables, so **re-running it deletes
  all data**. (`apply_migration.py --reset` refuses database names without "test".)
- `shared/types.ts` is types-only, so the status, shift and material labels exist in both
  `web/lib/labels.ts` and `mobile/lib/labels.ts`. `Record<Union, string>` makes type-check fail
  if a new value has no label.
- Checked with `ruff check` and `mypy --strict` (backend), `tsc` and `eslint` (web and mobile),
  an end-to-end API smoke test, and manual browser tests of web and of the mobile web build.
  The pull-to-refresh gesture still needs a device (Expo Go).

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
- **Which Python command to use (before the virtual environment exists):**
  - **macOS/Linux:** `python3`. There is no `python` command on these systems.
  - **Windows:** `python`. If it isn't found, use `py`, the Python launcher, which works even
    when `python` isn't on PATH.
  - Once the backend virtual environment is activated (step 3), plain `python` and `pip` work on
    every OS, so the later commands in this README use `python`.
- Run the doctor first (stdlib only, safe to run before installing anything). Expect a few
  FAILs until setup is done; run it again at the end with the backend venv activated:

```bash
# macOS/Linux
python3 scripts/doctor.py
```

```powershell
# Windows
python scripts/doctor.py      # if `python` is not found: py scripts/doctor.py
```

### 2. Start Postgres

**Option A — Docker (recommended)**

```bash
docker compose up -d prodlog-db
```

**Option B — local Postgres**

```bash
# macOS (Homebrew) — createdb runs as your own user by default
createdb production_log_test
```

```powershell
# Windows — the installer doesn't map your Windows user to a Postgres role;
# this prompts for the postgres password you set during install
createdb -U postgres production_log_test
```

```bash
# Linux — Postgres usually only trusts the `postgres` system user by default
sudo -u postgres createdb production_log_test
```

If `createdb` isn't on PATH, use pgAdmin or `psql` to create the database instead. On Linux, if
you'd rather have a role matching your own username (so plain `createdb` works), create one
first: `sudo -u postgres createuser -s $(whoami)`.

Then set `DATABASE_URL` in `backend/.env` (created in step 3) to your own user, password and
port. The Docker setup here uses port 5434 (not Postgres's default 5432) specifically so it
doesn't collide with a Postgres you may already have installed locally. A local install
typically uses 5432 by default — set that port in `DATABASE_URL` instead if you're using your
own local Postgres.

### 3. Backend

```bash
# bash (macOS/Linux)
cd backend
python3 -m venv .venv
source .venv/bin/activate     # from here on, `python` and `pip` exist (they are the venv's)
pip install -r requirements-dev.txt
cp .env.example .env          # edit DATABASE_URL if your credentials differ
python scripts/apply_migration.py
uvicorn main:app --reload

# PowerShell
cd backend
python -m venv .venv          # if `python` is not found, use: py -m venv .venv
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

The `python` commands above need the backend virtual environment activated, or Windows. On
macOS/Linux, outside the venv, run `python3 scripts/doctor.py` instead.

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

Find and stop whatever is using the port:
```bash
# macOS / Linux
lsof -i :8000
kill -9 <PID>
```
```powershell
# Windows (PowerShell)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```
Or just use a different port:
```bash
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

**Windows: `python` not found, "Python was not found; run without arguments to install from the Microsoft Store", or `python -m venv` fails**
`python` only works if Python's installer had "Add python.exe to PATH" ticked; otherwise
Windows' Microsoft Store stub (or a different Python such as Anaconda) answers instead. Use the
`py` launcher as an alternative to `python`; it doesn't depend on PATH:
```powershell
py --list                 # shows the Pythons installed on this machine
py -m venv .venv          # same as: python -m venv .venv
py scripts/doctor.py      # same as: python scripts/doctor.py
```
Pick a 3.10+ interpreter with `py -3.12 -m venv .venv` (use whichever version `py --list` shows).
After `.venv\Scripts\Activate.ps1`, plain `python` and `pip` work.

**PowerShell: `.venv\Scripts\Activate.ps1` blocked**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Wrong Node version**
- macOS/Linux: use [nvm](https://github.com/nvm-sh/nvm): `nvm install 20 && nvm use 20`.
- Windows: `nvm` (posix) doesn't work here — install
  [nvm-windows](https://github.com/coreybutler/nvm-windows) separately, then the same commands
  work: `nvm install 20` and `nvm use 20`.
- Or just download the right version directly from https://nodejs.org.

**`docker compose` not found**
Older Docker installs ship it as `docker-compose` (with a hyphen). Use that spelling, or
upgrade Docker Desktop.

## Fair game

- Adding dependencies is fine — add them to the appropriate requirements / package.json and
  explain your choice.
- Do not restructure the existing directory layout; the paths above are referenced in the
  invitation email.
- You may add your own agent-instruction files (CLAUDE.md, .cursorrules, etc.).
