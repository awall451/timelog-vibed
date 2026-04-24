from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import click
from tabulate import tabulate

from timelog import service

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
    # shell prompt box-drawing characters
    if any(ch in s for ch in ("╭", "╰", "λ", "│", "╮", "╱")):
        return False
    if s.startswith("<local-command-caveat>") or s.startswith("<command-name>"):
        return False
    return True


def _active_hours(timestamps: list[datetime]) -> float:
    if len(timestamps) < 2:
        return 0.0
    sorted_ts = sorted(timestamps)
    total = 0.0
    for i in range(1, len(sorted_ts)):
        gap = (sorted_ts[i] - sorted_ts[i - 1]).total_seconds()
        if gap < IDLE_THRESHOLD_SECS:
            total += gap
    return total / 3600


def _load_history(date_str: str) -> dict[tuple[str, str], RawSession]:
    if not HISTORY_FILE.exists():
        raise click.ClickException(f"No Claude history file found at {HISTORY_FILE}")

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


def _infer_category(display_texts: list[str], git_branches: list[str]) -> str:
    combined = " ".join(display_texts[:5]).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return category
    for branch in git_branches:
        for prefix, category in BRANCH_PREFIX_MAP.items():
            if branch.startswith(prefix):
                return category
    return "Development"


def _build_description(display_texts: list[str], max_chars: int = 120) -> str:
    parts = []
    for text in display_texts[:3]:
        sentence = re.split(r"[.!?\n]", text.strip())[0].strip()
        if sentence:
            parts.append(sentence)
    desc = "; ".join(parts)
    return desc[:max_chars] if len(desc) > max_chars else desc


def _ai_infer(
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
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        output = result.stdout.strip()
        # Strip markdown code fences if present
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


def _build_proposed_entries(date_str: str, use_ai: bool = True) -> list[ProposedEntry]:
    session_map = _load_history(date_str)

    by_project: dict[str, list[RawSession]] = {}
    for (project_path, _), session in session_map.items():
        by_project.setdefault(project_path, []).append(session)

    entries = []
    for project_path, sessions in by_project.items():
        all_timestamps = sorted(ts for s in sessions for ts in s.timestamps)
        all_displays: list[str] = []
        for s in sorted(sessions, key=lambda s: min(s.timestamps)):
            all_displays.extend(s.display_texts)

        _enrich_with_branches(sessions)
        all_branches = list({b for s in sessions for b in s.git_branches})

        hours = _active_hours(all_timestamps)
        if hours < 0.05:
            continue

        project_name = Path(project_path).name

        if use_ai:
            ai_result = _ai_infer(project_name, all_branches, all_displays)
            if ai_result:
                category, description = ai_result
            else:
                category = _infer_category(all_displays, all_branches)
                description = _build_description(all_displays)
        else:
            category = _infer_category(all_displays, all_branches)
            description = _build_description(all_displays)

        entries.append(ProposedEntry(
            date=date_str,
            project=project_name,
            category=category,
            description=description,
            hours=math.ceil(hours * 4) / 4,
            session_ids=[s.session_id for s in sessions],
        ))

    return sorted(entries, key=lambda e: e.project)


def _check_duplicates(
    entries: list[ProposedEntry],
) -> tuple[list[ProposedEntry], list[ProposedEntry]]:
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


def _print_entries_table(entries: list[ProposedEntry]) -> None:
    rows = [
        [e.project, e.category, e.hours, e.description]
        for e in entries
    ]
    click.echo(tabulate(rows, headers=["Project", "Category", "Hours", "Description"], tablefmt="psql"))


def _resolve_date(date: str | None) -> str:
    if date is None:
        return datetime.now().strftime("%Y-%m-%d")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise click.ClickException(f"Date must be in YYYY-MM-DD format, got: {date!r}")
    return date


@click.group("tlclaude", invoke_without_command=True)
@click.pass_context
def claude(ctx: click.Context) -> None:
    """Generate timelog entries from Claude Code session data."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@claude.command("sessions")
@click.option("--date", default=None, metavar="YYYY-MM-DD", help="Date to inspect (default: today)")
def sessions_cmd(date: str | None) -> None:
    """List raw Claude sessions for a date."""
    date_str = _resolve_date(date)
    session_map = _load_history(date_str)

    if not session_map:
        click.echo(f"No Claude sessions found for {date_str}.")
        return

    _enrich_with_branches(list(session_map.values()))

    rows = []
    for (project_path, session_id), session in sorted(
        session_map.items(), key=lambda kv: min(kv[1].timestamps)
    ):
        project_name = Path(project_path).name
        start = min(session.timestamps).strftime("%H:%M")
        hours = _active_hours(session.timestamps)
        branches = ", ".join(session.git_branches) or "—"
        rows.append([project_name, start, f"{hours:.2f}h", branches, session_id[:8]])

    click.echo(f"\nDate: {date_str}  ({len(session_map)} session{'s' if len(session_map) != 1 else ''})\n")
    click.echo(tabulate(rows, headers=["Project", "Start", "Active", "Branch", "Session"], tablefmt="psql"))


@claude.command("preview")
@click.option("--date", default=None, metavar="YYYY-MM-DD", help="Date to preview (default: today)")
@click.option("--no-ai", is_flag=True, default=False, help="Skip AI inference, use heuristics only")
def preview_cmd(date: str | None, no_ai: bool) -> None:
    """Show proposed timelog entries without inserting."""
    date_str = _resolve_date(date)

    if not no_ai:
        click.echo("Analyzing sessions with Claude... ", nl=False)

    entries = _build_proposed_entries(date_str, use_ai=not no_ai)

    if not no_ai:
        click.echo("done.")

    if not entries:
        click.echo(f"No Claude sessions found for {date_str}.")
        return

    click.echo(f"\nProposed entries for {date_str}:\n")
    _print_entries_table(entries)


@claude.command("sync")
@click.option("--date", default=None, metavar="YYYY-MM-DD", help="Date to sync (default: today)")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompt")
@click.option("--no-ai", is_flag=True, default=False, help="Skip AI inference, use heuristics only")
def sync_cmd(date: str | None, yes: bool, no_ai: bool) -> None:
    """Generate and insert timelog entries from Claude sessions."""
    date_str = _resolve_date(date)

    if not no_ai:
        click.echo("Analyzing sessions with Claude... ", nl=False)

    entries = _build_proposed_entries(date_str, use_ai=not no_ai)

    if not no_ai:
        click.echo("done.")

    if not entries:
        click.echo(f"No Claude sessions found for {date_str}.")
        return

    new_entries, skipped = _check_duplicates(entries)

    for e in skipped:
        click.echo(f"Skipping {e.project} — entry for {e.date} already exists.")

    if not new_entries:
        click.echo("All entries already synced.")
        return

    click.echo(f"\nProposed entries for {date_str}:\n")
    _print_entries_table(new_entries)
    click.echo()

    if not yes:
        click.confirm("Insert these entries?", abort=True)

    import sqlite3
    from timelog.db import DB_PATH
    try:
        for e in new_entries:
            service.add_entry(e.project, e.category, e.description, e.hours, e.date)
    except sqlite3.OperationalError as exc:
        if "readonly" in str(exc):
            raise click.ClickException(
                f"Database is read-only: {DB_PATH}\n"
                f"Fix: sudo chown $(whoami):$(whoami) {DB_PATH}"
            )
        raise

    n = len(new_entries)
    click.echo(f"Inserted {n} entr{'y' if n == 1 else 'ies'}.")
