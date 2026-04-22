# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A local time-tracking app: Python/FastAPI backend + SvelteKit frontend, both containerized. Data lives in `./data/timelog.db` (SQLite, bind-mounted). CLI commands forward into the API container via `docker compose exec`.

## Running the stack

```bash
source dev.sh     # loads tlstart / tlstop and tl* CLI wrappers into shell
tlstart           # docker compose up --build -d (builds on first run)
tlstop            # docker compose down
```

| Service  | URL                   |
|----------|-----------------------|
| Frontend | http://localhost:3000 |
| API      | http://localhost:8888 |

To rebuild after Python changes: `docker compose up --build -d api`  
To rebuild after frontend changes: `docker compose up --build -d frontend`

## Architecture

### Backend (`timelog/`)

Three-layer Python package installed as console scripts via `pyproject.toml`:

- **`db.py`** — raw SQLite via `sqlite3`. DB path from `TIMELOG_DB` env var (default `~/.local/share/timelog/timelog.db`; overridden to `/data/timelog.db` in the container). All queries use parameterized statements. `init_db()` creates the table on first call.
- **`service.py`** — all business logic. Calls `db.py` functions. Both entry queries and sum queries live here. `import_from_csv` does a full DELETE + re-insert (no upsert).
- **`api.py`** — FastAPI app. Thin wrappers over `service.py`. CORS allows `localhost:3000`, `5173`, `4173`. Entry model validated via Pydantic (`NewEntry`). `/import` accepts multipart CSV upload.
- **`cli/`** — Click commands (`tlshow`, `tlsum`, `tlupdate`, `tlexport`, `tlimport`, `tlhelp`). Each subcommand calls `service.py` directly and formats output with `tabulate`.

The console scripts defined in `pyproject.toml` (e.g. `tlshow = "timelog.cli.show:show"`) are installed into the container's PATH by `pip install .` in the Dockerfile.

### Frontend (`frontend/`)

SvelteKit app (Svelte 5 runes syntax). Single API client at `src/lib/api.ts` — all fetch calls go through `api.get/post` helpers with `VITE_API_BASE` override support. Three routes: `/` (dashboard), `/entries` (filterable table), `/log` (entry form).

Themes: six CSS custom property sets applied via `data-theme` on `<html>`, defined in `+layout.svelte`. Persisted to `localStorage`.

### Docker Compose

Two services — `api` and `frontend`. The `api` container sets `TIMELOG_DB=/data/timelog.db` and mounts `./data:/data`. Both mount `/etc/localtime` for host timezone. No inter-container networking needed (frontend hits the API at `localhost:8888` from the browser).

## Schema

Single table, auto-created by `db.init_db()`:

```sql
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project     TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    description TEXT,
    hours       REAL    NOT NULL CHECK (hours > 0),
    date        TEXT    NOT NULL DEFAULT (date('now'))
)
```

## Local development (outside Docker)

```bash
pip install -e .
TIMELOG_DB=./data/timelog.db tlserve   # API at localhost:8888

cd frontend
npm install
npm run dev                            # frontend at localhost:5173
```
