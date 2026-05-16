from __future__ import annotations

import math
import re
from datetime import datetime
from pathlib import Path

from timelog.ai_sync.ai_infer import ai_infer
from timelog.ai_sync.sources import claude as claude_source
from timelog.ai_sync.sources import cursor as cursor_source
from timelog.ai_sync.types import ProposedEntry, RawSession

ALL_SOURCES = ("claude", "cursor")

IDLE_THRESHOLD_SECS = 30 * 60

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


def active_hours(timestamps: list[datetime]) -> float:
    """Sum gaps between consecutive timestamps that are under IDLE_THRESHOLD_SECS.

    Operates over the union of all source timestamps for a project — overlapping
    minutes count once because the merged list is sorted before delta-summing.
    """
    if len(timestamps) < 2:
        return 0.0
    sorted_ts = sorted(timestamps)
    total = 0.0
    for i in range(1, len(sorted_ts)):
        gap = (sorted_ts[i] - sorted_ts[i - 1]).total_seconds()
        if gap < IDLE_THRESHOLD_SECS:
            total += gap
    return total / 3600


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


def _gather_sessions(date_str: str, sources: list[str]) -> list[RawSession]:
    raw: list[RawSession] = []
    if "claude" in sources:
        raw.extend(claude_source.load_sessions(date_str))
    if "cursor" in sources:
        raw.extend(cursor_source.load_sessions(date_str))
    return raw


def _assemble_entries(
    date_str: str,
    raw_sessions: list[RawSession],
    use_ai: bool,
) -> list[ProposedEntry]:
    by_project: dict[str, list[RawSession]] = {}
    for s in raw_sessions:
        project_name = Path(s.project_path).name
        by_project.setdefault(project_name, []).append(s)

    entries: list[ProposedEntry] = []
    for project_name, sessions in by_project.items():
        all_ts = sorted(ts for s in sessions for ts in s.timestamps)
        hours = active_hours(all_ts)
        if hours < 0.05:
            continue

        all_displays: list[str] = []
        for s in sorted(sessions, key=lambda s: min(s.timestamps) if s.timestamps else datetime.min):
            all_displays.extend(s.display_texts)
        all_branches = list({b for s in sessions for b in s.git_branches})
        sources_used = sorted({s.source for s in sessions})

        if use_ai:
            result = ai_infer(project_name, all_branches, all_displays)
            if result:
                category, description = result
            else:
                category = infer_category(all_displays, all_branches)
                description = build_description(all_displays)
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
            sources=sources_used,
        ))

    return sorted(entries, key=lambda e: e.project)


def build_proposed_entries(
    date_str: str,
    sources: list[str] | None = None,
) -> list[ProposedEntry]:
    """Heuristic-only entry proposals (no AI call)."""
    sources = list(sources) if sources is not None else list(ALL_SOURCES)
    raw = _gather_sessions(date_str, sources)
    return _assemble_entries(date_str, raw, use_ai=False)


def build_proposed_entries_with_ai(
    date_str: str,
    sources: list[str] | None = None,
) -> list[ProposedEntry]:
    """Entry proposals with Claude-CLI inference for category + description."""
    sources = list(sources) if sources is not None else list(ALL_SOURCES)
    raw = _gather_sessions(date_str, sources)
    return _assemble_entries(date_str, raw, use_ai=True)
