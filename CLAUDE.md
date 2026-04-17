# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important

This is a fork for experimentation. The original remote GitHub repository must remain completely untouched — do not push to it or suggest doing so. This fork is Claude-assisted; the original repo is the author's own independent work.

## What this is

A CLI time-tracking tool backed by a local PostgreSQL instance running in Docker. All user-facing functionality is bash functions/aliases defined in `timelog_functions.sh`, sourced into the user's shell. There is no build step, no test suite, and no package manager.

## Running the stack

```bash
docker compose up -d    # start the postgres container
docker compose down     # stop it
```

The container is named `timelog` (hardcoded in `compose.yml` and relied upon by every `docker exec` call in `timelog_functions.sh` — do not rename it).

## Loading functions into the shell

```bash
source timelog_functions.sh
```

Or for permanent installation, append to `~/.bashrc`:
```bash
readlink -f timelog_functions.sh | xargs echo "source $1" >> ~/.bashrc
```

## Architecture

Everything lives in two places:

- **`timelog_functions.sh`** — all bash functions (`tlshow`, `tlsum`, `tlupdate`, `tlexport`, `tlhelp`) and the `tlexec` alias. Each function shells out to `docker exec timelog psql -U admin -d timelog` with an inline SQL string. There is no ORM or query builder — SQL is constructed directly via string interpolation (single quotes are escaped manually before insertion).
- **`conf/create-table.sql`** — the schema, auto-run by postgres on first init via `docker-entrypoint-initdb.d`. The single table is `entries(id, project, category, description, hours, date)`. `conf/init-timezone.sql` sets the DB timezone to `America/Chicago`.

Data persists in `./pgdata/` (a bind-mounted host directory). Deleting `pgdata/` wipes all data.

## Credentials & configuration

Default credentials are set in `compose.yml`:
- `POSTGRES_USER`: `admin`
- `POSTGRES_PASSWORD`: `p@ssw0rd`
- `POSTGRES_DB`: `timelog`

If `POSTGRES_USER` or `POSTGRES_DB` are changed, they must also be updated in `timelog_functions.sh` (the `-U admin -d timelog` flags appear on every `docker exec` call). Credentials **must** be changed before the first `docker compose up` — changing them afterward has no effect on an already-initialized volume.

## Direct DB access

```bash
tlexec   # opens interactive psql session inside the container
```

Or raw:
```bash
docker exec -it timelog psql -U admin -d timelog
```
