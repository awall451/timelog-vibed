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

## Current Focus

**Core improvements first.** The personal app is the priority — make it genuinely great before touching enterprise. All planned features below are core (MIT, single-user) and build toward a polished, fun, informative tool. Enterprise is a far-future vision, not active work.

## Planned Features (Core — MIT)

### 1. Entries Page — GitHub-style Heatmap
52×7 SVG grid (last ~1 year), color intensity = hours logged per day. Pure SVG, no library. Filter-aware:
- Intensity derived from `allEntries` filtered by current `project` + `category` (not date)
- Clicking a cell sets `selectedDate` → table filters to that day + cell highlights
- Changing project/category filter → heatmap intensities re-derive reactively
- 5 intensity levels (0h, <2h, <4h, <6h, 6h+) using CSS vars for theme compat
- Month labels above columns, tooltip on hover (date + hours)
- No new API endpoint needed — all data already client-side in `allEntries`

### 2. Charts Page (`/charts`) — Analytics Dashboard
New route with multiple pure SVG/CSS charts, no charting library. Candidate charts:
- **Donut — Hours by Project** (all time or date-ranged)
- **Donut — Hours by Category**
- **Stacked bar — Daily hours last 14 days**, color segments per project
- **Weekly pace line** — daily hours vs 8h goal line, last 4 weeks (sparkline style)
- **Project × Category heatmap** — grid: rows=projects, cols=categories, cell=hours; shows where time actually goes
- Date range picker to scope all charts simultaneously
- Charts use same CSS vars as themes so they look native

### 3. Live Timer
Start/stop timer → auto-calculates hours on stop, pre-fills log form. Biggest UX gap vs Toggl. State persisted to `localStorage` so refresh doesn't lose it.

### 4. Entry Templates
Save common project+category+description combos. One-click to pre-fill log form. Stored in `localStorage`, no schema change needed.

### 5. Weekly Goal Tracking
Set target hours/week per project. Progress bar on dashboard. Config stored in `localStorage`.

### 6. Export (CSV + PDF)
CSV already exists via CLI (`tlexport`). Add PDF timesheet export from frontend — grouped by project, date range selectable. Uses browser print API or a lightweight lib.

### 7. Tags
Free-form labels on entries, filterable. Adds dimension without schema overhaul — stored as comma-separated text column, parsed client-side.

### 8. PWA / Mobile Layout
Service worker + manifest → installable, works offline for log form. Mobile-friendly layout for field logging.

## Future Vision — Multi-User / Team Edition

> **Not active work.** Long-term vision. Build core personal features first. Everything here is MIT open source — no closed source, no private repos. Single repo, one license.

Goal: same codebase, multi-user support opt-in via config. Default behavior = current single-user local app, unchanged.

### Mode Switch
`TIMELOG_MODE=single` (default) — no auth, no users table, current behavior exactly.  
`TIMELOG_MODE=multi` — enables auth middleware, user/org tables, admin routes.  
One env var. Personal users never notice the enterprise code exists.

### Architecture
```
timelog/
  db.py        ← schema adapts to mode (single vs multi)
  service.py   ← user_id=1 hardcoded in single mode
  api.py       ← auth middleware skipped in single mode
  auth/        ← OIDC middleware, only loaded in multi mode
  admin/       ← admin routes, only loaded in multi mode
  billing/     ← invoice engine, only loaded in multi mode
```

### Auth Strategy (multi mode)
OIDC via [Dex](https://dexidp.io/) — federates upstream IdPs via connectors:
- Self-hosted team: Dex sidecar → connector for LDAP/AD/SAML/Google Workspace
- Direct SSO: point `OIDC_ISSUER` at Google/Okta/Auth0 directly — same code path, no Dex required
- Local dev: Dex with static passwords connector
- One env var swap between Dex and any OIDC provider

### Multi-User DB Schema (additive — single mode uses only `entries`)
```sql
organizations(id, name, slug, billing_email)
users(id, org_id, email, oidc_sub, role, name)
  -- role: admin | manager | member
  -- no password_hash — OIDC only
projects(id, org_id, name, client, billing_rate, active)
categories(id, name)
entries(id, user_id, project_id, category_id, description, hours, date, approved_by, submitted_at)
invoices(id, org_id, project_id, period_start, period_end, pdf_path, generated_at)
```

### New Surface Area (multi mode)
- **Auth** — OIDC/JWT middleware, Dex or direct SSO
- **RBAC** — admin / manager / member views
- **Approval workflow** — submit → manager approves → entry locked
- **Billing engine** — hours × rate → invoice PDF (`weasyprint` or `reportlab`)
- **Admin dashboard** — cross-user views, utilization reports
- **Project budgets** — hour caps, alerts
- **Client portal** — read-only billed-hours view for clients
- **Slack/Teams bot** — `/log 2h ProjectX dev` → entry created
- **Rate cards** — $/hr per user or per project

### What stays shared (all modes)
- All frontend chart components (heatmap, donuts, bars) — scoped per-user in multi mode
- Live timer, entry templates
- Core entry CRUD logic — unchanged
- CLI — single mode only

### Monetization (future consideration)
Hosted SaaS: run `timelog.io`, charge $5-8/mo for convenience. Code stays MIT. No enterprise licensing complexity. Decide after the app has real users.

## Local development (outside Docker)

```bash
pip install -e .
TIMELOG_DB=./data/timelog.db tlserve   # API at localhost:8888

cd frontend
npm install
npm run dev                            # frontend at localhost:5173
```

## Known bugs to fix (CORS / easy-local-proxy)

When accessed via `timelog-vibed-frontend-1.localhost` (easy-local-proxy), the frontend breaks because `VITE_API_BASE` defaults to `http://localhost:8888` and `api.py` only allows `localhost:3000/5173/4173` origins — CORS blocks it.

**Current workaround** applied in `api.py`: `allow_origin_regex=r"http://.*\.localhost(:\d+)?"` — fine for local dev but not a real fix.

**Proper fix options (pick one):**
1. Change `VITE_API_BASE` default from `http://localhost:8888` to `/api` and proxy `/api/*` → API container via Caddy or the frontend's vite config. Same-origin → no CORS needed.
2. Pass `VITE_API_BASE=http://timelog-vibed-api-1.localhost` as a build arg and use `allow_origin_regex` as a permanent addition to the API.

Option 1 is cleaner. Vite proxy config in `frontend/vite.config.ts` would add:
```ts
server: { proxy: { '/api': 'http://localhost:8888' } }
```
And the production path needs Caddy to handle it too.

## Known bugs to fix

* Clock live track widget - if on the 'Log Time' page and click 'Stop & log,' nothing happens. Normal behavior is to redirect to the log time page, but this breaks if you are alread on the log time page.

## Visual improvements (future)

* Edit entry modal + Log Time form — native browser controls (number spinner on Hours, calendar icon on Date) look inconsistent with custom styling. Attempted fix with `appearance: textfield` + `::-webkit-calendar-picker-indicator` caused issues. Proper fix: replace `type="date"` with a text input + hidden date picker (same pattern as the filter bar's custom calendar button), and strip number spinner via `::-webkit-inner-spin-button { -webkit-appearance: none }`. Affects both `frontend/src/routes/entries/+page.svelte` (edit modal) and `frontend/src/routes/log/+page.svelte` (log form).
