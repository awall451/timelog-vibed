#!/usr/bin/env python3
"""Generate the hosted-demo seed database: one full year of plausible entries.

The demo re-years every row at load time (see frontend/src/lib/demo/db.ts), so
the seed only needs to cover every month-day once. Output is deterministic for
a given --seed, so the tracked frontend/seed/timelog.db is reproducible from a
fresh checkout.

Density is tuned to the sparse "Dec/Jan" look of the original real data:
~88% of weekdays active, ~45% of weekend days, mostly one entry per active
day, ~2.3 h/day. Holidays are nearly empty.

Usage:
    python3 scripts/gen-demo-seed.py                # writes frontend/seed/timelog.db
    python3 scripts/gen-demo-seed.py --seed 7 --year 2026 --out /tmp/x.db
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "scripts" / "demo-seed-corpus.json"
DEFAULT_OUT = ROOT / "frontend" / "seed" / "timelog.db"

P_ACTIVE_WEEKDAY = 0.88
P_ACTIVE_WEEKEND = 0.45
P_ACTIVE_HOLIDAY = 0.15
# entries per active day: weights for 1, 2, 3
ENTRIES_PER_DAY = ([1, 2, 3], [0.85, 0.13, 0.02])

SCHEMA = """
CREATE TABLE entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project     TEXT    NOT NULL,
                category    TEXT    NOT NULL,
                description TEXT,
                hours       REAL    NOT NULL CHECK (hours > 0),
                date        TEXT    NOT NULL DEFAULT (date('now'))
            )
"""


def holidays(year: int) -> set[dt.date]:
    nov1 = dt.date(year, 11, 1)
    # 4th Thursday of November + the Friday after
    first_thu = nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7)
    thanksgiving = first_thu + dt.timedelta(weeks=3)
    return {
        dt.date(year, 1, 1),
        dt.date(year, 7, 4),
        thanksgiving,
        thanksgiving + dt.timedelta(days=1),
        dt.date(year, 12, 24),
        dt.date(year, 12, 25),
        dt.date(year, 12, 26),
        dt.date(year, 12, 31),
    }


class Deck:
    """Draw corpus rows without replacement, reshuffling when exhausted."""

    def __init__(self, rows: list[dict], rng: random.Random):
        self.rows, self.rng, self.pile = rows, rng, []

    def draw(self) -> dict:
        if not self.pile:
            self.pile = self.rows[:]
            self.rng.shuffle(self.pile)
        return self.pile.pop()


def generate(year: int, seed: int, corpus: list[dict]) -> list[tuple]:
    rng = random.Random(seed)
    deck = Deck(corpus, rng)
    hol = holidays(year)
    out: list[tuple] = []
    day = dt.date(year, 1, 1)
    while day.year == year:
        if not (day.month == 2 and day.day == 29):  # never emit 02-29
            if day in hol:
                p = P_ACTIVE_HOLIDAY
            elif day.weekday() >= 5:
                p = P_ACTIVE_WEEKEND
            else:
                p = P_ACTIVE_WEEKDAY
            if rng.random() < p:
                n = rng.choices(*ENTRIES_PER_DAY)[0]
                for _ in range(n):
                    r = deck.draw()
                    out.append((r["project"], r["category"], r["description"], r["hours"], day.isoformat()))
        day += dt.timedelta(days=1)
    return out


def write_db(path: Path, rows: list[tuple]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.execute(SCHEMA)
    con.executemany(
        "INSERT INTO entries (project, category, description, hours, date) VALUES (?, ?, ?, ?, ?)", rows
    )
    con.commit()
    con.execute("VACUUM")
    con.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--year", type=int, default=2026, help="calendar year to generate (default 2026)")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed (default 42)")
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args()

    corpus = json.loads(a.corpus.read_text())
    rows = generate(a.year, a.seed, corpus)
    write_db(a.out, rows)
    days = len({r[4] for r in rows})
    hours = sum(r[3] for r in rows)
    print(f"{a.out}: {len(rows)} entries over {days} active days, {hours:.1f} h, year {a.year}, seed {a.seed}")


if __name__ == "__main__":
    main()
