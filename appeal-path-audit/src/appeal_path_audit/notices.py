"""Loads the notice text an organization actually sends when it renders an
adverse automated decision — the artifact `rules.py`'s corpus is checked
against. A notice is just a text file; its id is the filename stem, since
these are usually named for what they are (`loan-denial.txt`)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Notice:
    id: str
    text: str


def load_notices(notices_dir: Path) -> dict[str, Notice]:
    """Loads every `*.txt` file under `notices_dir` into `Notice` objects,
    keyed by filename stem. Raises ValueError if the directory has no
    notices to check — an empty audit isn't a passing one."""
    notices: dict[str, Notice] = {}
    for path in sorted(notices_dir.glob("*.txt")):
        notices[path.stem] = Notice(id=path.stem, text=path.read_text())
    if not notices:
        raise ValueError(f"{notices_dir}: no *.txt notice files found")
    return notices
