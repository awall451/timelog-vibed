from __future__ import annotations

from timelog import service
from timelog.ai_sync.types import ProposedEntry


def check_duplicates(
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
