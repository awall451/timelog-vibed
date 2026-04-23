import csv
from timelog.db import get_connection, init_db


def _ensure_init() -> None:
    init_db()


# ── Entry queries ──────────────────────────────────────────────────────────

def get_all_entries() -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM entries ORDER BY date, id").fetchall()
    return [dict(r) for r in rows]


def get_entries_today() -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE date = date('now') ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def get_entries_yesterday() -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE date = date('now', '-1 day') ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def get_last_entry() -> dict | None:
    _ensure_init()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM entries ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def get_entries_by_project(name: str) -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE project = ? ORDER BY date, id", (name,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_entries_by_category(name: str) -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE category = ? ORDER BY date, id", (name,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_entries_by_month(month: str) -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE strftime('%Y-%m', date) = ? ORDER BY date, id",
            (month,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_distinct_projects() -> list[str]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT project FROM entries ORDER BY project"
        ).fetchall()
    return [r["project"] for r in rows]


def get_distinct_categories() -> list[str]:
    _ensure_init()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM entries ORDER BY category"
        ).fetchall()
    return [r["category"] for r in rows]


# ── Sum queries ────────────────────────────────────────────────────────────

def sum_all() -> float:
    _ensure_init()
    with get_connection() as conn:
        row = conn.execute("SELECT COALESCE(SUM(hours), 0) FROM entries").fetchone()
    return row[0]


def sum_today() -> float:
    _ensure_init()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) FROM entries WHERE date = date('now')"
        ).fetchone()
    return row[0]


def sum_yesterday() -> float:
    _ensure_init()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) FROM entries WHERE date = date('now', '-1 day')"
        ).fetchone()
    return row[0]


def sum_by_month(month: str) -> float:
    _ensure_init()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) FROM entries WHERE strftime('%Y-%m', date) = ?",
            (month,)
        ).fetchone()
    return row[0]


def sum_by_project(name: str) -> float:
    _ensure_init()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) FROM entries WHERE project = ?", (name,)
        ).fetchone()
    return row[0]


def sum_by_category(name: str) -> float:
    _ensure_init()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) FROM entries WHERE category = ?", (name,)
        ).fetchone()
    return row[0]


def sum_per_project(month: str | None = None) -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        if month:
            rows = conn.execute(
                """SELECT project, SUM(hours) AS hours FROM entries
                   WHERE strftime('%Y-%m', date) = ?
                   GROUP BY project ORDER BY hours DESC""",
                (month,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT project, SUM(hours) AS hours FROM entries
                   GROUP BY project ORDER BY hours DESC"""
            ).fetchall()
    return [dict(r) for r in rows]


def sum_per_category(month: str | None = None) -> list[dict]:
    _ensure_init()
    with get_connection() as conn:
        if month:
            rows = conn.execute(
                """SELECT category, SUM(hours) AS hours FROM entries
                   WHERE strftime('%Y-%m', date) = ?
                   GROUP BY category ORDER BY hours DESC""",
                (month,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT category, SUM(hours) AS hours FROM entries
                   GROUP BY category ORDER BY hours DESC"""
            ).fetchall()
    return [dict(r) for r in rows]


# ── Write ──────────────────────────────────────────────────────────────────

def delete_entry(entry_id: int) -> None:
    _ensure_init()
    with get_connection() as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))


def update_entry(
    entry_id: int,
    project: str,
    category: str,
    description: str,
    hours: float,
    date: str,
) -> dict | None:
    _ensure_init()
    with get_connection() as conn:
        conn.execute(
            "UPDATE entries SET project=?, category=?, description=?, hours=?, date=? WHERE id=?",
            (project, category, description, hours, date, entry_id),
        )
        row = conn.execute("SELECT * FROM entries WHERE id=?", (entry_id,)).fetchone()
    return dict(row) if row else None


def add_entry(
    project: str,
    category: str,
    description: str,
    hours: float,
    date: str | None = None,
) -> None:
    _ensure_init()
    with get_connection() as conn:
        if date:
            conn.execute(
                "INSERT INTO entries (project, category, description, hours, date) VALUES (?, ?, ?, ?, ?)",
                (project, category, description, hours, date),
            )
        else:
            conn.execute(
                "INSERT INTO entries (project, category, description, hours) VALUES (?, ?, ?, ?)",
                (project, category, description, hours),
            )


# ── Import ─────────────────────────────────────────────────────────────────

def import_from_csv(filepath: str) -> int:
    _ensure_init()
    rows = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        expected = {"id", "project", "category", "description", "hours", "date"}
        if not expected.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must have columns: {', '.join(sorted(expected))}")
        for row in reader:
            rows.append((
                int(row["id"]),
                row["project"],
                row["category"],
                row["description"],
                float(row["hours"]),
                row["date"],
            ))
    with get_connection() as conn:
        conn.execute("DELETE FROM entries")
        conn.executemany(
            "INSERT INTO entries (id, project, category, description, hours, date) VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
    return len(rows)


# ── Export ─────────────────────────────────────────────────────────────────

def export_to_csv(filepath: str) -> None:
    entries = get_all_entries()
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "project", "category", "description", "hours", "date"]
        )
        writer.writeheader()
        writer.writerows(entries)
