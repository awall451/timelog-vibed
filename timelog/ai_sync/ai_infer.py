from __future__ import annotations

import glob
import json
import re
import shutil
import subprocess
from pathlib import Path

CLAUDE_APP_DIR = Path("/claude-app")  # mounted from ~/.local/share/claude in Docker


def _find_claude_bin() -> str:
    """Locate the claude binary — system PATH first, then the Docker mount."""
    if shutil.which("claude"):
        return "claude"
    versions = sorted(glob.glob(str(CLAUDE_APP_DIR / "versions" / "[0-9]*")))
    if versions:
        return versions[-1]
    return "claude"


VALID_CATEGORIES = {
    "Development",
    "Debugging",
    "Planning",
    "Documentation",
    "Testing",
    "Review",
}


def ai_infer(
    project: str, branches: list[str], excerpts: list[str]
) -> tuple[str, str] | None:
    """Call the Claude CLI to infer (category, description) for a project."""
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
        if category not in VALID_CATEGORIES:
            category = "Development"
        return category, description[:120] if description else ""
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError, OSError):
        return None
