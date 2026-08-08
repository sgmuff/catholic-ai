"""Loads and validates `principles/*.yaml` and `principles/non-negotiables.yaml`
so `eval/assessment.py` has something real to check a described AI use
against. Two distinct shapes, loaded separately: the eight graded principles
(matching `principles/schema.yaml`) and the bright-line gate items (matching
`principles/non-negotiables.yaml`'s own, smaller shape) — see
`rubric/criteria.md` for how the two stages differ.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

_NON_PRINCIPLE_FILES = frozenset({"schema.yaml", "non-negotiables.yaml"})
_REQUIRED_PRINCIPLE_FIELDS = ("id", "name", "magisterial_citations", "description")
_REQUIRED_CITATION_FIELDS = ("source", "reference")
_REQUIRED_ITEM_FIELDS = ("id", "title", "description", "citations")


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


def _citations_from(
    raw: object, source: Path, field: str = "magisterial_citations"
) -> tuple[Citation, ...]:
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{source}: '{field}' must be a non-empty list")
    citations = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValueError(f"{source}: each citation must be a mapping, got {entry!r}")  # noqa: TRY004
        missing = [f for f in _REQUIRED_CITATION_FIELDS if not entry.get(f)]
        if missing:
            raise ValueError(f"{source}: citation missing field(s) {missing}: {entry!r}")
        citations.append(Citation(source=str(entry["source"]), reference=str(entry["reference"])))
    return tuple(citations)


def _principle_from_dict(data: dict[str, object], source: Path) -> Principle:
    missing = [f for f in _REQUIRED_PRINCIPLE_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"{source}: missing required field(s) {missing}")
    return Principle(
        id=str(data["id"]),
        name=str(data["name"]),
        citations=_citations_from(data["magisterial_citations"], source),
        description=str(data["description"]).strip(),
    )


def load_principles(principles_dir: Path) -> dict[str, Principle]:
    """Loads every principle file under `principles_dir` (everything except
    `schema.yaml` and `non-negotiables.yaml`) into `Principle` objects, keyed
    by `id`. Raises ValueError, naming the offending file, if a principle is
    missing a required field — malformed principle data should fail loudly
    rather than let an assessment silently run against incomplete grounding.
    """
    principles: dict[str, Principle] = {}
    for path in sorted(principles_dir.glob("*.yaml")):
        if path.name in _NON_PRINCIPLE_FILES:
            continue
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")  # noqa: TRY004
        principle = _principle_from_dict(data, path)
        if principle.id in principles:
            raise ValueError(f"{path}: duplicate principle id {principle.id!r}")
        principles[principle.id] = principle
    return principles


def _non_negotiable_from_dict(data: dict[str, object], source: Path) -> NonNegotiable:
    missing = [f for f in _REQUIRED_ITEM_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"{source}: non-negotiable item missing field(s) {missing}: {data!r}")
    return NonNegotiable(
        id=str(data["id"]),
        title=str(data["title"]),
        description=str(data["description"]).strip(),
        citations=_citations_from(data["citations"], source, field="citations"),
    )


def _load_non_negotiables_file(principles_dir: Path) -> dict[str, object]:
    path = principles_dir / "non-negotiables.yaml"
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")  # noqa: TRY004
    return data


def load_non_negotiables(principles_dir: Path) -> tuple[NonNegotiable, ...]:
    """Loads `principles/non-negotiables.yaml`'s `items` list — the bright-line
    gate `eval/assessment.py` checks before the graded rubric runs. Each
    item carries its own `citations`, matching `magisterial_citations` on a
    graded `Principle` — see `NonNegotiable`.
    """
    path = principles_dir / "non-negotiables.yaml"
    data = _load_non_negotiables_file(principles_dir)
    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError(f"{path}: 'items' must be a non-empty list")
    non_negotiables = []
    seen_ids: set[str] = set()
    for entry in items:
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: each item must be a mapping, got {entry!r}")  # noqa: TRY004
        item = _non_negotiable_from_dict(entry, path)
        if item.id in seen_ids:
            raise ValueError(f"{path}: duplicate non-negotiable id {item.id!r}")
        seen_ids.add(item.id)
        non_negotiables.append(item)
    return tuple(non_negotiables)
