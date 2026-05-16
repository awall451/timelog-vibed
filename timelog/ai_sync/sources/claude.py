from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from timelog.ai_sync.types import RawSession

CLAUDE_DIR = Path.home() / ".claude"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"
PROJECTS_DIR = CLAUDE_DIR / "projects"


def _path_to_slug(path: str) -> str:
    return path.replace("/", "-").replace(".", "-")


def _is_meaningful_display(text: str) -> bool:
    s = text.strip()
    if not s or len(s) < 15:
        return False
    if s.lower() in ("init", "/exit", "yes", "no", "ok", "proceed", "y", "n"):
        return False
    if s.startswith("/"):
        return False
    if any(ch in s for ch in ("╭", "╰", "λ", "│", "╮", "╱")):
        return False
    if s.startswith("<local-command-caveat>") or s.startswith("<command-name>"):
        return False
    return True


def _enrich_with_branches(sessions: list[RawSession]) -> None:
    for s in sessions:
        slug = _path_to_slug(s.project_path)
        session_file = PROJECTS_DIR / slug / f"{s.session_id}.jsonl"
        if not session_file.exists():
            continue
        branches_seen: set[str] = set()
        try:
            with open(session_file) as f:
                for line in f:
                    try:
                        r = json.loads(line)
                        b = r.get("gitBranch", "")
                        if b and b not in ("HEAD", ""):
                            branches_seen.add(b)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue
        s.git_branches = list(branches_seen)


def load_sessions(date_str: str) -> list[RawSession]:
    """Load Claude Code sessions active on `date_str` from ~/.claude/history.jsonl."""
    if not HISTORY_FILE.exists():
        raise FileNotFoundError(str(HISTORY_FILE))

    result: dict[tuple[str, str], RawSession] = {}

    with open(HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts_ms = r.get("timestamp")
            project_path = r.get("project", "")
            session_id = r.get("sessionId", "")
            display = r.get("display", "")

            if not ts_ms or not project_path or not session_id:
                continue

            dt = datetime.fromtimestamp(ts_ms / 1000)
            if dt.strftime("%Y-%m-%d") != date_str:
                continue

            key = (project_path, session_id)
            if key not in result:
                result[key] = RawSession(
                    session_id=session_id,
                    project_path=project_path,
                    timestamps=[],
                    display_texts=[],
                    source="claude",
                )

            result[key].timestamps.append(dt)
            if _is_meaningful_display(display):
                result[key].display_texts.append(display)

    sessions = list(result.values())
    _enrich_with_branches(sessions)
    return sessions
