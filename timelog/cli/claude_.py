from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import click
from tabulate import tabulate

from timelog import service
from timelog.claude_service import (
    ProposedEntry,
    RawSession,
    active_hours,
    build_description,
    build_proposed_entries,
    check_duplicates,
    enrich_with_branches,
    infer_category,
    load_history,
)


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


def _build_proposed_entries_with_ai(date_str: str) -> list[ProposedEntry]:
    from timelog.claude_service import (
        PROJECTS_DIR,
        build_description,
        infer_category,
        load_history,
        enrich_with_branches,
        active_hours,
    )
    import math
    from pathlib import Path

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
        ai_result = _ai_infer(project_name, all_branches, all_displays)
        if ai_result:
            category, description = ai_result
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
    try:
        session_map = load_history(date_str)
    except FileNotFoundError as e:
        raise click.ClickException(f"Claude history not found: {e}")

    if not session_map:
        click.echo(f"No Claude sessions found for {date_str}.")
        return

    enrich_with_branches(list(session_map.values()))

    rows = []
    for (project_path, session_id), session in sorted(
        session_map.items(), key=lambda kv: min(kv[1].timestamps)
    ):
        project_name = Path(project_path).name
        start = min(session.timestamps).strftime("%H:%M")
        hours = active_hours(session.timestamps)
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

    try:
        entries = _build_proposed_entries_with_ai(date_str) if not no_ai else build_proposed_entries(date_str)
    except FileNotFoundError as e:
        raise click.ClickException(f"Claude history not found: {e}")

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

    try:
        entries = _build_proposed_entries_with_ai(date_str) if not no_ai else build_proposed_entries(date_str)
    except FileNotFoundError as e:
        raise click.ClickException(f"Claude history not found: {e}")

    if not no_ai:
        click.echo("done.")

    if not entries:
        click.echo(f"No Claude sessions found for {date_str}.")
        return

    new_entries, skipped = check_duplicates(entries)

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
