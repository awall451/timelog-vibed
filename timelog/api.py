import tempfile
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from timelog import service
from timelog import ai_sync
from timelog.ai_sync import build_proposed_entries_with_ai

app = FastAPI(title="Timelog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:3000"],
    allow_origin_regex=r"http://.*\.localhost(:\d+)?",  # TODO: see CLAUDE.md for proper fix
    allow_methods=["*"],
    allow_headers=["*"],
)


class NewEntry(BaseModel):
    project: str
    category: str
    description: str = ""
    hours: float = Field(gt=0)
    date: str | None = None


# ── Entries ────────────────────────────────────────────────────────────────

@app.get("/entries")
def get_all_entries():
    return service.get_all_entries()


@app.get("/entries/today")
def get_entries_today():
    return service.get_entries_today()


@app.get("/entries/yesterday")
def get_entries_yesterday():
    return service.get_entries_yesterday()


@app.get("/entries/last")
def get_last_entry():
    entry = service.get_last_entry()
    if not entry:
        raise HTTPException(status_code=404, detail="No entries found")
    return entry


@app.get("/entries/month/{month}")
def get_entries_by_month(month: str):
    return service.get_entries_by_month(month)


@app.get("/entries/project/{name}")
def get_entries_by_project(name: str):
    return service.get_entries_by_project(name)


@app.get("/entries/category/{name}")
def get_entries_by_category(name: str):
    return service.get_entries_by_category(name)


@app.post("/entries", status_code=201)
def add_entry(entry: NewEntry):
    service.add_entry(
        entry.project, entry.category, entry.description, entry.hours, entry.date
    )
    return {"status": "created"}


@app.put("/entries/{entry_id}")
def update_entry(entry_id: int, entry: NewEntry):
    result = service.update_entry(
        entry_id, entry.project, entry.category, entry.description, entry.hours,
        entry.date or ""
    )
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result


@app.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int):
    service.delete_entry(entry_id)


# ── Sums ───────────────────────────────────────────────────────────────────

@app.get("/sum")
def sum_all():
    return {"hours": service.sum_all()}


@app.get("/sum/today")
def sum_today():
    return {"hours": service.sum_today()}


@app.get("/sum/yesterday")
def sum_yesterday():
    return {"hours": service.sum_yesterday()}


@app.get("/sum/month/{month}")
def sum_by_month(month: str):
    return {"hours": service.sum_by_month(month)}


@app.get("/sum/projects")
def sum_per_project(month: str | None = None):
    return service.sum_per_project(month)


@app.get("/sum/project/{name}")
def sum_by_project(name: str):
    return {"hours": service.sum_by_project(name)}


@app.get("/sum/categories")
def sum_per_category(month: str | None = None):
    return service.sum_per_category(month)


@app.get("/sum/category/{name}")
def sum_by_category(name: str):
    return {"hours": service.sum_by_category(name)}


@app.post("/import", status_code=200)
def import_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    try:
        count = service.import_from_csv(tmp_path)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        os.unlink(tmp_path)
    return {"imported": count}


# ── AI Sync ────────────────────────────────────────────────────────────────

VALID_SOURCES = {"claude", "cursor"}

_MOUNT_HINTS = {
    "claude": '"- ~/.claude:/root/.claude:ro"',
    "cursor": '"- ~/.cursor:/root/.cursor:ro"',
}


class AiSyncEntry(BaseModel):
    project: str
    category: str
    description: str = ""
    hours: float = Field(gt=0)


class AiSyncRequest(BaseModel):
    date: str
    entries: list[AiSyncEntry]


# Legacy aliases — kept so external callers using /claude/* don't break.
ClaudeEntry = AiSyncEntry
ClaudeSyncRequest = AiSyncRequest


def _parse_sources(raw: str | None) -> list[str]:
    if not raw:
        return ["claude", "cursor"]
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    invalid = [p for p in parts if p not in VALID_SOURCES]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source(s): {invalid}. Allowed: {sorted(VALID_SOURCES)}",
        )
    return parts or ["claude", "cursor"]


def _run_preview(date_str: str, sources: list[str]) -> dict:
    try:
        entries = build_proposed_entries_with_ai(date_str, sources)
    except FileNotFoundError as exc:
        missing = str(exc)
        which = "claude" if ".claude" in missing else "cursor" if ".cursor" in missing else None
        hint = _MOUNT_HINTS.get(which, "")
        raise HTTPException(
            status_code=503,
            detail=(
                f"AI source history not found: {missing}. "
                f"Mount the host directory into the api container "
                f"(add {hint} to the api volumes in docker-compose.yml) "
                f"and run tlstart to rebuild."
            ),
        )
    _, skipped = ai_sync.check_duplicates(entries)
    skipped_keys = {(e.project, e.date) for e in skipped}
    for e in entries:
        if (e.project, e.date) in skipped_keys:
            e.already_exists = True
    return {"date": date_str, "entries": [
        {
            "project": e.project,
            "category": e.category,
            "description": e.description,
            "hours": e.hours,
            "already_exists": e.already_exists,
            "sources": e.sources,
        }
        for e in entries
    ]}


@app.get("/ai-sync/preview")
def ai_sync_preview(date: str | None = None, sources: str | None = None):
    date_str = date or datetime.now().strftime("%Y-%m-%d")
    return _run_preview(date_str, _parse_sources(sources))


@app.post("/ai-sync/sync")
def ai_sync_sync(body: AiSyncRequest):
    for e in body.entries:
        service.add_entry(e.project, e.category, e.description, e.hours, body.date)
    return {"inserted": len(body.entries)}


# Legacy endpoints — pre-multi-source clients. New work should use /ai-sync/*.
@app.get("/claude/preview")
def claude_preview(date: str | None = None):
    date_str = date or datetime.now().strftime("%Y-%m-%d")
    return _run_preview(date_str, ["claude"])


@app.post("/claude/sync")
def claude_sync(body: ClaudeSyncRequest):
    return ai_sync_sync(body)


def run():
    import uvicorn
    uvicorn.run("timelog.api:app", host="127.0.0.1", port=8888)


# ── Meta ───────────────────────────────────────────────────────────────────

@app.get("/projects")
def get_projects():
    return service.get_distinct_projects()


@app.get("/categories")
def get_categories():
    return service.get_distinct_categories()
