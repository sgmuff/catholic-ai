"""Loads and validates `rules/*.yaml` — the corpus of disclosure
requirements `runner.py` checks each notice against. Each file groups rules
from one legal framework; each entry names which mechanical check
(`checks.py`) applies and what it's looking for.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from appeal_path_audit.checks import CHECKS

_REQUIRED_FIELDS = ("id", "framework", "description", "severity", "check")
_VALID_SEVERITIES = frozenset({"high", "medium", "low"})


@dataclass(frozen=True)
class Rule:
    id: str
    framework: str
    description: str
    severity: str
    check: str
    check_args: dict[str, object]


def _rule_from_dict(data: dict[str, object], source: Path) -> Rule:
    missing = [f for f in _REQUIRED_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"{source}: rule missing required field(s) {missing}: {data!r}")

    severity = data["severity"]
    if severity not in _VALID_SEVERITIES:
        raise ValueError(
            f"{source}: rule {data['id']!r} severity {severity!r} must be one of "
            f"{sorted(_VALID_SEVERITIES)}"
        )

    check = data["check"]
    if check not in CHECKS:
        raise ValueError(
            f"{source}: rule {data['id']!r} references unknown check {check!r}; "
            f"must be one of {sorted(CHECKS)}"
        )

    check_args = data.get("check_args") or {}
    if not isinstance(check_args, dict):
        raise ValueError(f"{source}: rule {data['id']!r} 'check_args' must be a mapping")  # noqa: TRY004

    return Rule(
        id=str(data["id"]),
        framework=str(data["framework"]),
        description=str(data["description"]).strip(),
        severity=str(severity),
        check=str(check),
        check_args=check_args,
    )


def load_rules(rules_dir: Path) -> dict[str, Rule]:
    """Loads every rule across every `rules_dir/*.yaml` file into `Rule`
    objects, keyed by id. Raises ValueError, naming the offending file and
    rule id, on anything malformed — including a missing or empty
    directory, since an audit that silently checked zero rules isn't a
    passing one."""
    rules: dict[str, Rule] = {}
    for path in sorted(rules_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")  # noqa: TRY004
        items = data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError(f"{path}: 'items' must be a non-empty list")
        for entry in items:
            if not isinstance(entry, dict):
                raise ValueError(f"{path}: each item must be a mapping, got {entry!r}")  # noqa: TRY004
            rule = _rule_from_dict(entry, path)
            if rule.id in rules:
                raise ValueError(f"{path}: duplicate rule id {rule.id!r}")
            rules[rule.id] = rule
    if not rules:
        raise ValueError(f"{rules_dir}: no rule files found")
    return rules
