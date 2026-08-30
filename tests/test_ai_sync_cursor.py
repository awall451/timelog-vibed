from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from timelog.ai_sync import aggregator
from timelog.ai_sync.sources import cursor as cursor_source
from timelog.ai_sync.types import RawSession


def _build_cursor_db(db_path: Path, rows: list[tuple[str, str, str, int]]) -> None:
    """rows: (hash, conversationId, fileName, timestamp_ms)"""
    con = sqlite3.connect(db_path)
    con.execute(
        """
        CREATE TABLE ai_code_hashes (
            hash TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            fileExtension TEXT,
            fileName TEXT,
            requestId TEXT,
            conversationId TEXT,
            timestamp INTEGER,
            model TEXT,
            createdAt INTEGER NOT NULL
        )
        """
    )
    for h, conv, fname, ts in rows:
        con.execute(
            "INSERT INTO ai_code_hashes VALUES (?, 'cli', NULL, ?, NULL, ?, ?, NULL, ?)",
            (h, fname, conv, ts, ts),
        )
    con.commit()
    con.close()


def test_cursor_source_loads_sessions_with_workspace_from_filename_prefix(tmp_path: Path) -> None:
    db = tmp_path / "ai-code-tracking.db"
    target_dt = datetime(2026, 5, 14, 10, 30)
    ts_ms = int(target_dt.timestamp() * 1000)
    _build_cursor_db(db, [
        ("h1", "conv-A", "/home/dillon/lab/timelog-vibed/timelog/api.py", ts_ms),
        ("h2", "conv-A", "/home/dillon/lab/timelog-vibed/frontend/src/lib/api.ts", ts_ms + 60_000),
        ("h3", "conv-B", "/opt/git/other-project/src/main.go", ts_ms + 5_000),
        ("h4", "conv-B", "/opt/git/other-project/README.md", ts_ms + 6_000),
    ])

    with patch.object(cursor_source, "CURSOR_DB", db), \
         patch.object(cursor_source, "CURSOR_PROJECTS_DIR", tmp_path / "no-such-dir"):
        sessions = cursor_source.load_sessions("2026-05-14")

    sessions.sort(key=lambda s: s.session_id)
    assert [s.session_id for s in sessions] == ["conv-A", "conv-B"]
    assert sessions[0].project_path == "/home/dillon/lab/timelog-vibed"
    assert sessions[0].source == "cursor"
    assert len(sessions[0].timestamps) == 2
    assert sessions[1].project_path == "/opt/git/other-project"


def test_cursor_source_filters_by_date(tmp_path: Path) -> None:
    db = tmp_path / "ai-code-tracking.db"
    on_date = int(datetime(2026, 5, 14, 12, 0).timestamp() * 1000)
    off_date = int(datetime(2026, 5, 13, 12, 0).timestamp() * 1000)
    _build_cursor_db(db, [
        ("h1", "conv-A", "/repo/file.py", on_date),
        ("h2", "conv-B", "/repo/file.py", off_date),
    ])

    with patch.object(cursor_source, "CURSOR_DB", db), \
         patch.object(cursor_source, "CURSOR_PROJECTS_DIR", tmp_path / "no-such-dir"):
        sessions = cursor_source.load_sessions("2026-05-14")

    assert [s.session_id for s in sessions] == ["conv-A"]


def test_cursor_source_missing_db_raises_filenotfound(tmp_path: Path) -> None:
    nonexistent = tmp_path / "missing.db"
    with patch.object(cursor_source, "CURSOR_DB", nonexistent):
        with pytest.raises(FileNotFoundError):
            cursor_source.load_sessions("2026-05-14")


def test_aggregator_union_of_intervals_no_double_count() -> None:
    """Two sources covering the same project in overlapping minutes:
    merged active hours must equal the union span, not the sum."""
    base = datetime(2026, 5, 14, 9, 0)
    minute = timedelta(minutes=1)

    claude_session = RawSession(
        session_id="claude-1",
        project_path="/home/dillon/repo",
        timestamps=[base + minute * i for i in range(0, 11)],  # 09:00 .. 09:10
        display_texts=["fixing a bug in the api"],
        source="claude",
    )
    cursor_session = RawSession(
        session_id="cursor-1",
        project_path="/home/dillon/repo",
        timestamps=[base + minute * i for i in range(5, 16)],  # 09:05 .. 09:15
        display_texts=["adding tests for the api"],
        source="cursor",
    )

    entries = aggregator._assemble_entries(
        "2026-05-14",
        [claude_session, cursor_session],
        use_ai=False,
    )

    assert len(entries) == 1
    e = entries[0]
    assert e.project == "repo"
    assert sorted(e.sources) == ["claude", "cursor"]
    # Union span 09:00–09:15 = 15 min ≈ 0.25h. Quarter-hour ceil → 0.25.
    # If we naively summed per-source hours we'd get ≈ 0.34h which would
    # round up to 0.5 — so 0.25 here proves the union path.
    assert e.hours == 0.25


def test_aggregator_source_filter_excludes_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    claude_session = RawSession(
        session_id="c1",
        project_path="/x/proj",
        timestamps=[datetime(2026, 5, 14, 9, 0), datetime(2026, 5, 14, 9, 10)],
        display_texts=["work"],
        source="claude",
    )
    cursor_session = RawSession(
        session_id="cu1",
        project_path="/x/other",
        timestamps=[datetime(2026, 5, 14, 9, 0), datetime(2026, 5, 14, 9, 10)],
        display_texts=["work"],
        source="cursor",
    )

    monkeypatch.setattr(aggregator.claude_source, "load_sessions", lambda _d: [claude_session])
    monkeypatch.setattr(aggregator.cursor_source, "load_sessions", lambda _d: [cursor_session])

    claude_only = aggregator.build_proposed_entries("2026-05-14", sources=["claude"])
    cursor_only = aggregator.build_proposed_entries("2026-05-14", sources=["cursor"])
    both = aggregator.build_proposed_entries("2026-05-14", sources=["claude", "cursor"])

    assert {e.project for e in claude_only} == {"proj"}
    assert {e.project for e in cursor_only} == {"other"}
    assert {e.project for e in both} == {"proj", "other"}
