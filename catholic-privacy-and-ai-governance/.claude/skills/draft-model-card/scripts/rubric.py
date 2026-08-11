"""Reads scoring parameters directly out of rubric/criteria.md rather than
duplicating them as a Python constant that could drift from the authored
rubric — the same single-source-of-truth discipline build-plan.md §3 applies
to the framework registry, applied here to the rubric.
"""

from __future__ import annotations

import re
from pathlib import Path

_DIMENSION_HEADING_RE = re.compile(r"^## \d+\.\s.+`([a-z][a-z0-9-]*)`\s*$", re.MULTILINE)
_THRESHOLD_RE = re.compile(r"Passing threshold:\s*(\d+)")


class RubricError(Exception):
    """Raised when rubric/criteria.md doesn't have the shape this project
    expects — a broken rubric, not a broken assessment.
    """


def load_dimension_ids(criteria_path: Path) -> list[str]:
    """Extracts every dimension id from criteria.md's own numbered headings
    (e.g. "## 1. Necessity and proportionality — `necessity-and-proportionality`"),
    in the order they appear.
    """
    text = criteria_path.read_text(encoding="utf-8")
    ids = _DIMENSION_HEADING_RE.findall(text)
    if not ids:
        raise RubricError(f"No dimension headings found in {criteria_path}")
    return ids


def load_passing_threshold(criteria_path: Path) -> int:
    """Extracts the "Passing threshold: N" value stated in criteria.md's own
    scoring instructions.
    """
    text = criteria_path.read_text(encoding="utf-8")
    match = _THRESHOLD_RE.search(text)
    if not match:
        raise RubricError(f"No passing threshold stated in {criteria_path}")
    return int(match.group(1))
