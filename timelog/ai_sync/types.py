from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Source = Literal["claude", "cursor"]


@dataclass
class RawSession:
    session_id: str
    project_path: str
    timestamps: list[datetime]
    display_texts: list[str]
    source: Source
    git_branches: list[str] = field(default_factory=list)


@dataclass
class ProposedEntry:
    date: str
    project: str
    category: str
    description: str
    hours: float
    session_ids: list[str]
    sources: list[str]
    already_exists: bool = False
