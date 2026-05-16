"""AI Sync — propose timelog entries from AI coding-assistant session history.

Sources today: Claude Code (`~/.claude`) and Cursor (`~/.cursor`). Linux only.
"""
from timelog.ai_sync.types import ProposedEntry, RawSession
from timelog.ai_sync.aggregator import (
    ALL_SOURCES,
    active_hours,
    build_description,
    build_proposed_entries,
    build_proposed_entries_with_ai,
    infer_category,
)
from timelog.ai_sync.duplicates import check_duplicates
from timelog.ai_sync.ai_infer import ai_infer
from timelog.ai_sync.sources import claude as claude_source
from timelog.ai_sync.sources import cursor as cursor_source

__all__ = [
    "ALL_SOURCES",
    "ProposedEntry",
    "RawSession",
    "active_hours",
    "ai_infer",
    "build_description",
    "build_proposed_entries",
    "build_proposed_entries_with_ai",
    "check_duplicates",
    "claude_source",
    "cursor_source",
    "infer_category",
]
