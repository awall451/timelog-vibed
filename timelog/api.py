from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from timelog import service

app = FastAPI(title="Timelog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
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
