"""Reads baseline-item ids directly out of a baselines/*.md document rather
than duplicating them as a Python constant that could drift from the
authored baseline — the same single-source-of-truth discipline
rubric.py applies to rubric/criteria.md, applied here to a vendor-review
baseline (build-plan.md step 16).
"""

from __future__ import annotations

import re
from pathlib import Path

_ITEM_HEADING_RE = re.compile(r"^## \d+\.\s.+`([a-z][a-z0-9-]*)`\s*$", re.MULTILINE)


class BaselineError(Exception):
    """Raised when a baselines/*.md file doesn't have the shape this
    project expects — a broken baseline document, not a broken review.
    """


def load_baseline_item_ids(baseline_path: Path) -> list[str]:
    """Extracts every baseline-item id from the document's own numbered
    headings (e.g. "## 1. Written data-processing terms — `dpa-in-place`"),
    in the order they appear.
    """
    text = baseline_path.read_text(encoding="utf-8")
    ids = _ITEM_HEADING_RE.findall(text)
    if not ids:
        raise BaselineError(f"No baseline-item headings found in {baseline_path}")
    return ids
