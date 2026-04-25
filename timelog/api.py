import tempfile
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from timelog import service
from timelog import claude_service
from timelog.claude_service import build_proposed_entries_with_ai

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


# ── Claude AI Sync ─────────────────────────────────────────────────────────

class ClaudeEntry(BaseModel):
    project: str
    category: str
    description: str = ""
    hours: float = Field(gt=0)


class ClaudeSyncRequest(BaseModel):
    date: str
    entries: list[ClaudeEntry]


@app.get("/claude/preview")
def claude_preview(date: str | None = None):
    date_str = date or datetime.now().strftime("%Y-%m-%d")
    try:
        entries = build_proposed_entries_with_ai(date_str)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Claude history not found. "
                "Mount ~/.claude into the container by adding "
                "\"- ~/.claude:/root/.claude:ro\" to the api volumes in docker-compose.yml, "
                "then run tlstart to rebuild."
            ),
        )
    new_entries, skipped = claude_service.check_duplicates(entries)
    for e in skipped:
        e.already_exists = True
    return {"date": date_str, "entries": [
        {
            "project": e.project,
            "category": e.category,
            "description": e.description,
            "hours": e.hours,
            "already_exists": e.already_exists,
        }
        for e in entries
    ]}


@app.post("/claude/sync")
def claude_sync(body: ClaudeSyncRequest):
    for e in body.entries:
        service.add_entry(e.project, e.category, e.description, e.hours, body.date)
    return {"inserted": len(body.entries)}


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
