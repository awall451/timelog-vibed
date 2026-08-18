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

## Demo build (stateless, browser-only)

Separate, self-contained Docker image for hosting a public demo. Live at **https://timelog.sigilworks.dev** (Azure Static Web Apps Free, deployed by `azure-pipelines.yml` — see `docs/demo-hosting.md`). Same source tree as the main app, gated on `VITE_DEMO_MODE=true`. Each visitor gets an isolated copy of the tracked seed DB at `frontend/seed/timelog.db` running as in-browser SQLite (`sql.js` WASM), persisted to that visitor's IndexedDB. Mutations never cross between visitors. There is no API server.

```bash
docker compose -f docker-compose.demo.yml up --build -d   # serves on :3002
```

The main `Dockerfile`, `docker-compose.yml`, and `tlstart` flow are untouched.

### How the swap works

- **`frontend/svelte.config.js`** — branches the adapter on `process.env.VITE_DEMO_MODE`. Demo build → `@sveltejs/adapter-static` with `fallback: 'index.html'`. Main build → `@sveltejs/adapter-node` (unchanged).
- **`frontend/src/routes/+layout.ts`** — `export const ssr = !import.meta.env.VITE_DEMO_MODE;` (SSR off in demo only — adapter-static can't SSR sql.js).
- **`frontend/src/lib/api.ts`** — `export const api = import.meta.env.VITE_DEMO_MODE ? (await import('./demo/api')).api : realApi;`. The dynamic import + top-level await keeps `sql.js` and the demo shim out of the main bundle (verified: 0 wasm assets in main `build/`).
- **`frontend/src/lib/demo/db.ts`** — `sql.js` init via `initSqlJs({ locateFile: () => sqlWasmUrl })`, fetches `/seed/timelog.db` on first load, hydrates from IndexedDB key `timelog-demo-db-v1` on subsequent loads, persists after every mutation, exposes `reset()`.
- **`frontend/src/lib/demo/api.ts`** — same shape as `realApi`. Each method runs the SQL string from `service.py` against sql.js. **Critical:** sql.js's `date('now','localtime')` runs in UTC, not host TZ — the shim binds `new Date().toLocaleDateString('sv-SE')` for today/yesterday queries instead of relying on `'localtime'`.
- **`frontend/src/lib/demo/csvImport.ts`** — pure-browser CSV parse (no PapaParse), DELETE + bulk INSERT against the in-memory DB. Mirrors `service.import_from_csv`.

### What's disabled in demo mode

- **AI Sync** — `/sync` and `/settings/ai-sync` render a "local-only feature" placeholder. Nav link in `+layout.svelte` gated on `!import.meta.env.VITE_DEMO_MODE`. The `api.claude.*` shim methods throw if called.
- **CSV import via API** — there's no API; use the in-browser parser from `csvImport.ts` if/when a UI button is wired up on `/settings/storage`.
- **All CLI commands** — they shell into the API container which doesn't exist in the demo deploy.

### Demo image pipeline

- **`frontend/Dockerfile.demo`** — multi-stage. Stage 1 (node:20-alpine) copies `frontend/` (which includes the tracked `frontend/seed/timelog.db`) and copies that seed into `static/seed/timelog.db`, then runs `npm run build:demo`. Stage 2 (`nginx:alpine`) serves `build/` via `nginx.demo.conf`. The local `data/timelog.db` working DB is NOT used by the demo build — the demo seed is a separate tracked file, **generated** by `scripts/gen-demo-seed.py` (see "Demo seed + date rotation" below) so the demo image is reproducible from a fresh checkout. Never hand-copy `data/timelog.db` over the seed.
- **`frontend/nginx.demo.conf`** — SPA fallback (`try_files $uri $uri/ /index.html`), gzip on JS/CSS/wasm, immutable cache for `/_app/immutable/`. **Do NOT add a `types {}` block** — it replaces the default mime map and breaks `text/html` serving (the index ends up as `application/octet-stream` and the browser downloads it instead of rendering).
- **`docker-compose.demo.yml`** — single `demo` service, `build.context: .` + `dockerfile: frontend/Dockerfile.demo`, port `3002:80`, no volumes, no env vars. Compose project name shares `timelog-vibed` with the main stack so orphan warnings about `api`/`frontend` are expected.
- **`.dockerignore`** at repo root — excludes `.git`, `node_modules`, `.svelte-kit`, `build`, `frontend/static/seed`, etc. from the demo build context. The main build (`context: ./frontend`) is unaffected.

### Adding new features

Because the demo and main builds share one source tree, every UI feature added to a route or component automatically appears in the demo. The only file that needs updating per backend change is `frontend/src/lib/demo/api.ts` — add a matching method whenever `timelog/api.py` gains a new endpoint that the frontend calls. The `api` shape in `api.ts` and `demo/api.ts` must stay in lockstep.

### Demo seed + date rotation

The seed is one full generated year of entries and is **re-yeared on every load** so the demo never goes stale:

- **`scripts/gen-demo-seed.py`** — deterministic generator (stdlib only). Draws project/category/description/hours from `scripts/demo-seed-corpus.json` (180 rows exported from the original real data, month names scrubbed) and lays them over calendar year 2026 with a sparse profile (~88% weekdays active, ~45% weekend days, mostly 1 entry/day, holidays nearly empty). Never emits `02-29`. Same `--seed` ⇒ byte-identical rows. Regenerate with `python3 scripts/gen-demo-seed.py` and commit `frontend/seed/timelog.db`. Edit the corpus JSON to change vocabulary; bump `--seed` to reshuffle.
- **`reyear()` in `frontend/src/lib/demo/db.ts`** — runs inside `getDb()` right after the DB is opened (fresh seed *and* IndexedDB-hydrated copies): `year = (MM-DD <= today's MM-DD) ? thisYear : thisYear - 1`, so every row lands in the trailing 365-day window ending today. Idempotent/stateless (`WHERE date <> new_date` guard; persists only when rows changed). `02-29` rows are skipped. Visitor-added entries are re-yeared too (harmless). Known trade-off: same MM-DD ⇒ weekday drifts by one each year.
- **`api.entries.last`** orders by `date DESC, id DESC` — after re-yearing, highest `id` is no longer the newest date.
- **`tests/e2e/demo-rotation.spec.ts`** — guards it: newest date within 6 days of today, nothing in the future, window spans a year.

### Resetting demo data

Settings → Data → "Reset demo data" (visible only in demo build). Deletes the IndexedDB key and reloads → next page load falls back to fetching `/seed/timelog.db`.

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

### Already shipped

- **Entries Page — GitHub-style Heatmap.** 52×7 SVG grid (last ~1 year), color intensity = hours logged per day, filter-aware. Pure SVG, no library. Lives in `frontend/src/routes/entries/+page.svelte`.
- **Charts Page (`/charts`) — Analytics Dashboard.** Donuts, daily stacked bars, weekly pace, project × category heatmap — pure SVG/CSS. Date-range picker scopes all charts.
- **Live Timer.** Start/stop widget; on stop, pre-fills the log form via `localStorage` `timer-prefill`. State persisted across reloads. Lives in `frontend/src/lib/TimerWidget.svelte`.

### Next up — agreed order

#### 1. Export — PDF timesheet
CSV already exists via CLI (`tlexport`). Add PDF export from the frontend — grouped by project, date range selectable. Browser print API or a small lib. Affects `/entries` (export button) or a new `/export` modal.

#### 2. Entry Templates
Save common project + category + description combos. One-click to pre-fill the log form. Stored in `localStorage`, no schema change. Settings page to manage templates; quick-pick UI on `/log`.

#### 3. Tags
Free-form labels on entries, filterable. Adds a dimension without a schema overhaul — comma-separated text column on `entries`, parsed client-side. Filter UI on `/entries` and a tag-aware breakdown on `/charts`.

#### 4. PWA / Mobile Layout
Service worker + manifest → installable, works offline for the log form. Mobile-friendly layout for field logging. Mobile horizontal-overflow fixes already in (commit `8dde8d4`); PWA install + offline log form is the remaining work.

### Security hygiene — supply chain & image scanning

Tracks `trivy image` findings against the production `timelog-vibed-frontend` container. **Root cause for the May 2026 scan:** all 11 HIGH CVEs (`cross-spawn`, `glob`, `minimatch`, `tar`) lived inside `usr/local/lib/node_modules/npm/node_modules/...` — i.e. they shipped with the **npm CLI bundled into `node:20-alpine`**, not from our app's `package.json`. Our own dep tree was already clean (`npm audit` shows zero HIGH/CRITICAL). Runtime risk in `node build` is nil since npm is never invoked at request time; the findings are scanner-surface noise driven by what the base image happens to ship.

**Done:**
- **Bumped frontend base image to `node:22-alpine`** (`frontend/Dockerfile`, `frontend/Dockerfile.demo`). node:22 ships npm 10.9.7 which drops the 11 vulnerable transitive deps from the previous npm 10.8.2. Re-scan confirms 11 HIGH → 1 HIGH (only `picomatch` 4.0.3 remains in bundled npm; fixed in npm ≥ 11.14.0).
- **Added npm `overrides` block** in `frontend/package.json` pinning `cross-spawn ≥7.0.5`, `glob ≥10.5.0`, `minimatch ≥9.0.7`, `tar ≥7.5.3`. Currently no-op against today's dep tree (modern `@sveltejs/kit` + `vite 8` no longer pull these in) but defense-in-depth for future transitive bumps.

**Next:**
- **Eliminate the last `picomatch` HIGH.** Either `RUN npm install -g npm@latest` in the final stage of `frontend/Dockerfile`, or drop npm from the final image entirely by copying pruned `node_modules` from the builder (`npm prune --omit=dev` in builder, `COPY --from=builder /app/node_modules ./node_modules` in the runtime stage, no `npm install` step). The latter is cleaner and shrinks the image.
- **Pin base image digest.** Replace `FROM node:22-alpine` with `node:22-alpine@sha256:...` so scans are reproducible and unattended `:latest`-style drift can't smuggle regressions back in.
- **Trivy in CI.** Add a job to `.github/workflows/ci.yml` that builds the frontend image and runs `trivy image --severity HIGH,CRITICAL --exit-code 1`. Fails PRs that introduce new HIGH/CRITICAL CVEs without an explicit allow-list entry.
- **Renovate or Dependabot.** Auto-PR transitive bumps and base-image bumps so the overrides block + manual base bumps aren't the only mitigation paths. Group dev-dep bumps weekly to keep PR noise low.

### Backlogged — defer until Team Mode

- **Weekly Goal Tracking (per-project).** Originally planned as `localStorage` config: per-project hours/week target with a dashboard progress bar. **Backlogged because** in single-user mode this is a subjective self-target with limited daily lift; the same problem is much better solved in team mode as **manager-allocated hours** — a project manager allocates X hours to a team member over Y days, with both sides tracking progress against that allocation. Re-evaluate once team mode lands and reuse the allocation primitive instead of building a single-user shim that gets thrown away. Daily goal (already in settings) is enough for single-user pacing.

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
- **Hour allocations** — manager allocates X hours to a team member over Y days for a project; both sides track progress against the allocation. **Subsumes the backlogged single-user "Weekly Goal Tracking" feature** — weekly goals were really just self-set allocations; in team mode the allocation primitive is real (set by a manager, scoped to a project, time-bounded) and the same UI surfaces it on the personal dashboard.
- **Billing engine** — hours × rate → invoice PDF (`weasyprint` or `reportlab`)
- **Admin dashboard** — cross-user views, utilization reports
- **Project budgets** — hour caps, alerts (org-level cousin of allocations)
- **Client portal** — read-only billed-hours view for clients
- **Slack/Teams bot** — `/log 2h ProjectX dev` → entry created
- **Rate cards** — $/hr per user or per project

### What stays shared (all modes)
- All frontend chart components (heatmap, donuts, bars) — scoped per-user in multi mode
- Live timer, entry templates
- Core entry CRUD logic — unchanged
- CLI — single mode only

### AI Sync / `tlclaude` — multi-node strategy (TBD)

**Today (single mode):** The AI Sync page and `tlclaude` CLI both depend on the API container having direct read access to the host's `~/.claude` directory (session JSONL files) and `~/.local/share/claude` (the `claude` binary). Both are bind-mounted in `docker-compose.yml`. This is the fast path and works perfectly for one user on one machine.

**The problem in multi mode:** Each user's Claude Code session data lives on their own laptop. A central API server has no way to read it. We need to design how this feature works — or whether it works — for hosted/team deployments before building it.

**Options to evaluate (pick one before implementing):**

1. **Local-only feature, gated by mode** — In `TIMELOG_MODE=multi`, hide the AI Sync page and disable `/claude/preview` and `/claude/sync` endpoints entirely. Simplest path. Users who want AI Sync run a local single-mode instance and POST entries to the team server via API.
2. **Local sidecar agent per user** — A small daemon installed on each user's machine reads `~/.claude`, summarizes sessions (project, timestamps, branches, sanitized excerpts), and uploads structured proposals to the team server. Server runs `ai_infer` against its own LLM key. Preserves the `/sync` page UX. Requires a separate install step per user.
3. **Browser-side parsing** — User picks their `.claude` folder via the File System Access API; the browser parses `history.jsonl` and POSTs structured session data. No server-side file access, no sidecar, but conversation excerpts traverse the network — privacy and excerpt-redaction policy must be airtight.
4. **Standalone desktop app** — Ship AI Sync as an Electron/Tauri app that runs the existing pipeline locally and pushes finished entries to the team server. Server stays oblivious to Claude. Highest engineering cost.

**Recommendation:** Start with option 1 when multi mode lands. Revisit options 2 or 3 if users actually ask for AI Sync in team deployments. Until then, AI Sync ships as a single-mode-only feature and is documented as such in the README.

### Monetization (future consideration)
Hosted SaaS: run `timelog.io`, charge $5-8/mo for convenience. Code stays MIT. No enterprise licensing complexity. Decide after the app has real users.

## Cross-browser testing

Playwright is configured at `frontend/playwright.config.ts` with multiple project flavors:

- **Mobile-overflow sweep** (Chromium-only): `razr-portrait`, `iphone-se`, `pixel-7`, `tablet` — runs `mobile-sweep.spec.ts` + `entries-mobile.spec.ts` to catch horizontal overflow regressions.
- **Smoke renders** (Chromium + Firefox at iPhone 13 + Pixel 7): `chromium-iphone-13`, `firefox-iphone-13`, `chromium-pixel-7`, `firefox-pixel-7` — runs `smoke-renders.spec.ts`, asserts every public route renders its h1 within 5s with no console errors. Catches blank-on-load failure modes (the bug class that motivated removing top-level await for iOS Safari < 15).
- **Demo recording** (`desktop-record`): runs `demo-recording.spec.ts` only, produces the screencast in `frontend/static/demo.webm` via `npm run record:demo`.

Default `npm run test:e2e` runs the mobile sweep + smoke renders across all the above projects. Recording is opt-in via `npm run record:demo`.

### WebKit (Safari engine) — CI-only on rolling distros

Playwright's WebKit Linux binary links against `libicu.so.74`, which Arch / openSUSE Tumbleweed / other rolling distros do not ship (they have ICU 76+). The repo handles this in two layers:

1. **GitHub Actions CI** (`.github/workflows/ci.yml`) — Ubuntu runner has libicu74 by default, so WebKit projects are added to `playwright.config.ts` automatically when `process.env.CI` is set. Every PR + push to main runs the smoke spec on `webkit-iphone-13` + `webkit-iphone-se` alongside the Chromium/Firefox projects. This gives us real Safari-engine coverage we can't run on the local Arch host.
2. **Local Docker** (when needed) — run from the official Playwright image:

   ```bash
   docker run --rm --network host -v $PWD:/work -w /work/frontend \
     mcr.microsoft.com/playwright:v1.59.1-noble \
     bash -c "CI=true npx playwright test --project=webkit-iphone-13 smoke-renders"
   ```

3. **Real-device coverage** for old iOS Safari (12, 13, 14) still requires BrowserStack / LambdaTest / Sauce Labs — Linux can't run iOS Simulator (Xcode is macOS-only) and Playwright's WebKit is always recent. This is the only way to catch parse-time regressions specific to a particular iOS version.

## Testing practice

For new behavior, prefer test-first (red → green) where the contract is clear: pure functions, derived values, api shapes, route smoke. Skip TDD for refactors, exploratory UI work, and one-line fixes. The `smoke-renders.spec.ts` exists specifically to catch the kind of silent regression that overflow/layout tests can't surface (e.g. the iOS Safari < 15 top-level await blank-page bug).

When CI fails on a PR, that's the signal to add a test that captures the bug before fixing the bug. Ratchet up coverage; don't drift.

## Local development (outside Docker)

```bash
pip install -e .
TIMELOG_DB=./data/timelog.db tlserve   # API at localhost:8888

cd frontend
npm install
npm run dev                            # frontend at localhost:5173
```

## Known bugs and follow-ups

Tracked in GitHub Issues — search `is:open` on the repo. Open at the time of this writing:

- [#28 — Mobile layout: unified responsive pass needed](https://github.com/awall451/timelog-vibed/issues/28)
- [#29 — Timer "Stop & Log" no-op when already on /log](https://github.com/awall451/timelog-vibed/issues/29)
- [#30 — Theme flash edge case on rapid hard-refresh in Firefox](https://github.com/awall451/timelog-vibed/issues/30)
- [#31 — CORS workaround: replace `allow_origin_regex` with same-origin proxy](https://github.com/awall451/timelog-vibed/issues/31)
- [#32 — Edit modal + Log form: native control styling inconsistencies](https://github.com/awall451/timelog-vibed/issues/32)

When you find a new bug, open an issue rather than appending to this file. Link the fixing PR via `Closes #N` in the description.
