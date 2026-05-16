from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from timelog.ai_sync.types import RawSession

# Linux path. macOS/Windows stubs for future support — not active yet.
CURSOR_HOME = Path.home() / ".cursor"
CURSOR_DB = CURSOR_HOME / "ai-tracking" / "ai-code-tracking.db"
CURSOR_PROJECTS_DIR = CURSOR_HOME / "projects"

# Future cross-platform paths (uncomment + branch on platform.system() when adding):
# macOS:   ~/Library/Application Support/Cursor/ai-tracking/ai-code-tracking.db
# Windows: %APPDATA%/Cursor/ai-tracking/ai-code-tracking.db

# Strip Cursor's <timestamp>...</timestamp> and <user_query>...</user_query> wrappers.
_TS_TAG = re.compile(r"<timestamp>.*?</timestamp>", re.DOTALL)
_QUERY_OPEN = re.compile(r"<user_query>\s*", re.IGNORECASE)
_QUERY_CLOSE = re.compile(r"\s*</user_query>", re.IGNORECASE)


def _path_to_slug(path: str) -> str:
    """Mirror Cursor's directory-naming scheme: '/opt/git/IVAAP' → 'opt-git-IVAAP'."""
    return path.replace("/", "-").replace(".", "-").lstrip("-")


def _common_path_prefix(paths: list[str]) -> str:
    """Longest common directory prefix across `paths` (component-wise, not char-wise)."""
    if not paths:
        return ""
    parts_list = [p.split("/") for p in paths]
    common: list[str] = []
    for parts_at_i in zip(*parts_list):
        if len(set(parts_at_i)) == 1:
            common.append(parts_at_i[0])
        else:
            break
    prefix = "/".join(common)
    return prefix if prefix.startswith("/") else "/" + prefix.lstrip("/") if prefix else ""


def _clean_transcript_text(text: str) -> str:
    text = _TS_TAG.sub("", text)
    text = _QUERY_OPEN.sub("", text)
    text = _QUERY_CLOSE.sub("", text)
    return text.strip()


def _load_transcript_excerpts(workspace_path: str, conversation_id: str) -> list[str]:
    """Read user-role messages from the agent transcript JSONL for `conversation_id`.

    Falls back to a directory scan if the slug-derived path doesn't exist —
    Cursor's slugger occasionally diverges from `_path_to_slug`.
    """
    if not CURSOR_PROJECTS_DIR.exists():
        return []

    slug = _path_to_slug(workspace_path)
    candidate = CURSOR_PROJECTS_DIR / slug / "agent-transcripts" / conversation_id
    transcript_dirs: list[Path] = []
    if candidate.exists():
        transcript_dirs.append(candidate)
    else:
        for project_dir in CURSOR_PROJECTS_DIR.iterdir():
            t = project_dir / "agent-transcripts" / conversation_id
            if t.exists():
                transcript_dirs.append(t)
                break

    excerpts: list[str] = []
    for tdir in transcript_dirs:
        for jsonl in sorted(tdir.glob("*.jsonl")):
            try:
                with open(jsonl) as f:
                    for line in f:
                        try:
                            rec = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if rec.get("role") != "user":
                            continue
                        msg = rec.get("message") or {}
                        content = msg.get("content") if isinstance(msg, dict) else None
                        if not isinstance(content, list):
                            continue
                        for part in content:
                            if not isinstance(part, dict):
                                continue
                            if part.get("type") == "text":
                                cleaned = _clean_transcript_text(str(part.get("text", "")))
                                if cleaned and len(cleaned) >= 15:
                                    excerpts.append(cleaned)
            except OSError:
                continue
    return excerpts


def load_sessions(date_str: str) -> list[RawSession]:
    """Load Cursor agent/composer sessions active on `date_str`.

    Reads `~/.cursor/ai-tracking/ai-code-tracking.db`. Each conversationId becomes
    one RawSession; workspace path is derived from the longest common prefix of
    `ai_code_hashes.fileName` values for that conversation.
    """
    if not CURSOR_DB.exists():
        raise FileNotFoundError(str(CURSOR_DB))

    con = sqlite3.connect(f"file:{CURSOR_DB}?mode=ro", uri=True)
    try:
        cur = con.cursor()
        cur.execute(
            """
            SELECT conversationId, fileName, timestamp
              FROM ai_code_hashes
             WHERE conversationId IS NOT NULL
               AND timestamp IS NOT NULL
               AND date(timestamp/1000, 'unixepoch', 'localtime') = ?
            """,
            (date_str,),
        )
        rows = cur.fetchall()
    finally:
        con.close()

    by_conv: dict[str, dict] = {}
    for conv_id, file_name, ts_ms in rows:
        if not conv_id or not file_name or not ts_ms:
            continue
        entry = by_conv.setdefault(
            conv_id,
            {"file_names": set(), "timestamps": []},
        )
        entry["file_names"].add(file_name)
        entry["timestamps"].append(datetime.fromtimestamp(ts_ms / 1000))

    sessions: list[RawSession] = []
    for conv_id, data in by_conv.items():
        file_names = [fn for fn in data["file_names"] if fn.startswith("/")]
        if not file_names:
            continue
        workspace_path = _common_path_prefix(file_names)
        # When the common prefix lands on a real file (e.g. single-file conv,
        # or all rows touched the same file), step up to its parent directory
        # so the workspace is always a directory.
        if workspace_path in data["file_names"]:
            workspace_path = str(Path(workspace_path).parent)
        if not workspace_path or workspace_path in ("/", ""):
            continue
        excerpts = _load_transcript_excerpts(workspace_path, conv_id)
        sessions.append(
            RawSession(
                session_id=conv_id,
                project_path=workspace_path,
                timestamps=data["timestamps"],
                display_texts=excerpts,
                source="cursor",
            )
        )

    return sessions
