"""Loads this skill's bundled `references/principles.json` and
`references/non-negotiables.json` — the portable, dependency-free
counterpart to this repo's `eval/principles.py`, which parses the same
content from `principles/*.yaml` via pyyaml. Generated from
`eval/sync_skill_bundle.py`'s `PORTABLE_PRINCIPLES_SOURCE` — do not hand-edit.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Citation:
    source: str
    reference: str


@dataclass(frozen=True)
class Principle:
    id: str
    name: str
    citations: tuple[Citation, ...]
    description: str


@dataclass(frozen=True)
class NonNegotiable:
    id: str
    title: str
    description: str
    citations: tuple[Citation, ...]


def _citations_from(raw: list[dict[str, str]]) -> tuple[Citation, ...]:
    return tuple(Citation(source=c["source"], reference=c["reference"]) for c in raw)


def load_principles(principles_dir: Path) -> dict[str, Principle]:
    data = json.loads((principles_dir / "principles.json").read_text())
    principles: dict[str, Principle] = {}
    for entry in data["principles"]:
        principles[entry["id"]] = Principle(
            id=entry["id"],
            name=entry["name"],
            citations=_citations_from(entry["magisterial_citations"]),
            description=entry["description"],
        )
    return principles


def load_non_negotiables(principles_dir: Path) -> tuple[NonNegotiable, ...]:
    data = json.loads((principles_dir / "non-negotiables.json").read_text())
    return tuple(
        NonNegotiable(
            id=entry["id"],
            title=entry["title"],
            description=entry["description"],
            citations=_citations_from(entry["citations"]),
        )
        for entry in data["items"]
    )
