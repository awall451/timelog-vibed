from __future__ import annotations

import glob
import json
import math
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from timelog import service

CLAUDE_APP_DIR = Path("/claude-app")  # mounted from ~/.local/share/claude in Docker


def _find_claude_bin() -> str:
    """Locate the claude binary — system PATH first, then the Docker mount."""
    import shutil
    if shutil.which("claude"):
        return "claude"
    versions = sorted(glob.glob(str(CLAUDE_APP_DIR / "versions" / "[0-9]*")))
    if versions:
        return versions[-1]
    return "claude"

IDLE_THRESHOLD_SECS = 30 * 60
CLAUDE_DIR = Path.home() / ".claude"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"
PROJECTS_DIR = CLAUDE_DIR / "projects"

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Debugging":     ["fix", "bug", "error", "debug", "broken", "crash", "traceback", "exception", "issue"],
    "Planning":      ["plan", "design", "architect", "approach", "strategy", "roadmap", "brainstorm"],
    "Documentation": ["doc", "readme", "comment", "explain", "document", "write up"],
    "Testing":       ["test", "spec", "coverage", "assert", "pytest", "unit"],
    "Review":        ["review", "refactor", "clean", "optimize", "simplify", "improve"],
}

BRANCH_PREFIX_MAP: dict[str, str] = {
    "fix/":      "Debugging",
    "bug/":      "Debugging",
    "hotfix/":   "Debugging",
    "feat/":     "Development",
    "feature/":  "Development",
    "docs/":     "Documentation",
    "doc/":      "Documentation",
    "test/":     "Testing",
    "refactor/": "Review",
}


@dataclass
class RawSession:
    session_id: str
    project_path: str
    timestamps: list[datetime]
    display_texts: list[str]
    git_branches: list[str] = field(default_factory=list)


@dataclass
class ProposedEntry:
    date: str
    project: str
    category: str
    description: str
    hours: float
    session_ids: list[str]
    already_exists: bool = False


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


def active_hours(timestamps: list[datetime]) -> float:
    if len(timestamps) < 2:
        return 0.0
    sorted_ts = sorted(timestamps)
    total = 0.0
    for i in range(1, len(sorted_ts)):
        gap = (sorted_ts[i] - sorted_ts[i - 1]).total_seconds()
        if gap < IDLE_THRESHOLD_SECS:
            total += gap
    return total / 3600


def load_history(date_str: str) -> dict[tuple[str, str], RawSession]:
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
                )

            result[key].timestamps.append(dt)
            if _is_meaningful_display(display):
                result[key].display_texts.append(display)

    return result


def enrich_with_branches(sessions: list[RawSession]) -> None:
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


def infer_category(display_texts: list[str], git_branches: list[str]) -> str:
    combined = " ".join(display_texts[:5]).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return category
    for branch in git_branches:
        for prefix, category in BRANCH_PREFIX_MAP.items():
            if branch.startswith(prefix):
                return category
    return "Development"


def build_description(display_texts: list[str], max_chars: int = 120) -> str:
    parts = []
    for text in display_texts[:3]:
        sentence = re.split(r"[.!?\n]", text.strip())[0].strip()
        if sentence:
            parts.append(sentence)
    desc = "; ".join(parts)
    return desc[:max_chars] if len(desc) > max_chars else desc


def ai_infer(
    project: str, branches: list[str], excerpts: list[str]
) -> tuple[str, str] | None:
    branch_str = ", ".join(branches) if branches else "main"
    excerpt_str = "\n".join(f"- {e[:200]}" for e in excerpts[:5])
    prompt = (
        "Given these conversation excerpts from a coding session, return JSON only — no other text.\n"
        'Keys: "category" (one of: Development, Debugging, Planning, Documentation, Testing, Review)\n'
        '      "description" (one sentence, max 120 chars, what was worked on)\n\n'
        f"Project: {project}\n"
        f"Git branches: {branch_str}\n"
        f"Conversation excerpts (chronological):\n{excerpt_str}"
    )
    try:
        result = subprocess.run(
            [_find_claude_bin(), "-p", prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        output = result.stdout.strip()
        if output.startswith("```"):
            output = re.sub(r"^```[a-z]*\n?", "", output)
            output = re.sub(r"\n?```$", "", output)
        data = json.loads(output)
        category = str(data.get("category", "")).strip()
        description = str(data.get("description", "")).strip()
        valid_categories = {"Development", "Debugging", "Planning", "Documentation", "Testing", "Review"}
        if category not in valid_categories:
            category = "Development"
        return category, description[:120] if description else ""
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError, OSError):
        return None


def build_proposed_entries(date_str: str) -> list[ProposedEntry]:
    session_map = load_history(date_str)

    by_project: dict[str, list[RawSession]] = {}
    for (project_path, _), session in session_map.items():
        by_project.setdefault(project_path, []).append(session)

    entries = []
    for project_path, sessions in by_project.items():
        all_timestamps = sorted(ts for s in sessions for ts in s.timestamps)
        all_displays: list[str] = []
        for s in sorted(sessions, key=lambda s: min(s.timestamps)):
            all_displays.extend(s.display_texts)

        enrich_with_branches(sessions)
        all_branches = list({b for s in sessions for b in s.git_branches})

        hours = active_hours(all_timestamps)
        if hours < 0.05:
            continue

        entries.append(ProposedEntry(
            date=date_str,
            project=Path(project_path).name,
            category=infer_category(all_displays, all_branches),
            description=build_description(all_displays),
            hours=math.ceil(hours * 4) / 4,
            session_ids=[s.session_id for s in sessions],
        ))

    return sorted(entries, key=lambda e: e.project)


def build_proposed_entries_with_ai(date_str: str) -> list[ProposedEntry]:
    session_map = load_history(date_str)

    by_project: dict[str, list[RawSession]] = {}
    for (project_path, _), session in session_map.items():
        by_project.setdefault(project_path, []).append(session)

    entries = []
    for project_path, sessions in by_project.items():
        all_timestamps = sorted(ts for s in sessions for ts in s.timestamps)
        all_displays: list[str] = []
        for s in sorted(sessions, key=lambda s: min(s.timestamps)):
            all_displays.extend(s.display_texts)

        enrich_with_branches(sessions)
        all_branches = list({b for s in sessions for b in s.git_branches})

        hours = active_hours(all_timestamps)
        if hours < 0.05:
            continue

        project_name = Path(project_path).name
        result = ai_infer(project_name, all_branches, all_displays)
        if result:
            category, description = result
        else:
            category = infer_category(all_displays, all_branches)
            description = build_description(all_displays)

        entries.append(ProposedEntry(
            date=date_str,
            project=project_name,
            category=category,
            description=description,
            hours=math.ceil(hours * 4) / 4,
            session_ids=[s.session_id for s in sessions],
        ))

    return sorted(entries, key=lambda e: e.project)


def check_duplicates(entries: list[ProposedEntry]) -> tuple[list[ProposedEntry], list[ProposedEntry]]:
    new_entries: list[ProposedEntry] = []
    skipped: list[ProposedEntry] = []
    for entry in entries:
        existing = service.get_entries_for_date(entry.date)
        already_exists = any(
            e["project"].lower() == entry.project.lower() for e in existing
        )
        if already_exists:
            skipped.append(entry)
        else:
            new_entries.append(entry)
    return new_entries, skipped
