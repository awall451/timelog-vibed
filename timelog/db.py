import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".local" / "share" / "timelog" / "timelog.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project     TEXT    NOT NULL,
                category    TEXT    NOT NULL,
                description TEXT,
                hours       REAL    NOT NULL CHECK (hours > 0),
                date        TEXT    NOT NULL DEFAULT (date('now'))
            )
        """)
