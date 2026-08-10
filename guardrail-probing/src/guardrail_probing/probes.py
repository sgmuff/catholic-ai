"""Loads and validates `probes/*.yaml` — the adversarial corpus `runner.py`
runs against a target. Each file is one category; each entry is one probe,
given either as a single-turn `prompt` or a multi-turn `turns` list (used by
the prompt-injection category to simulate attacker-controlled content
arriving as a tool result) — exactly one of the two, never both, never
neither.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from guardrail_probing.detectors import DETECTORS
from guardrail_probing.targets import Turn

_REQUIRED_FIELDS = ("id", "category", "severity", "detector")
_VALID_SEVERITIES = frozenset({"high", "medium", "low"})


@dataclass(frozen=True)
class Probe:
    id: str
    category: str
    severity: str
    turns: tuple[Turn, ...]
    detector: str
    detector_args: dict[str, object]


def _turns_from(data: dict[str, object], source: Path) -> tuple[Turn, ...]:
    prompt = data.get("prompt")
    turns = data.get("turns")
    probe_id = data.get("id")

    if prompt and turns:
        raise ValueError(f"{source}: probe {probe_id!r} has both 'prompt' and 'turns' — give one")
    if not prompt and not turns:
        raise ValueError(
            f"{source}: probe {probe_id!r} has neither 'prompt' nor 'turns' — give one"
        )

    if prompt:
        if not isinstance(prompt, str):
            raise ValueError(f"{source}: probe {probe_id!r} 'prompt' must be a string")
        return ({"role": "user", "content": prompt},)

    if not isinstance(turns, list) or not turns:
        raise ValueError(f"{source}: probe {probe_id!r} 'turns' must be a non-empty list")
    built: list[Turn] = []
    for entry in turns:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("role"), str)
            or not isinstance(entry.get("content"), str)
        ):
            raise ValueError(  # noqa: TRY004
                f"{source}: probe {probe_id!r} each turn needs a string 'role' and 'content': {entry!r}"
            )
        if entry["role"] not in ("user", "assistant", "tool"):
            raise ValueError(
                f"{source}: probe {probe_id!r} turn role {entry['role']!r} must be "
                "'user', 'assistant', or 'tool'"
            )
        built.append({"role": entry["role"], "content": entry["content"]})
    return tuple(built)


def _probe_from_dict(data: dict[str, object], source: Path) -> Probe:
    missing = [f for f in _REQUIRED_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"{source}: probe missing required field(s) {missing}: {data!r}")

    severity = data["severity"]
    if severity not in _VALID_SEVERITIES:
        raise ValueError(
            f"{source}: probe {data['id']!r} severity {severity!r} must be one of {sorted(_VALID_SEVERITIES)}"
        )

    detector = data["detector"]
    if detector not in DETECTORS:
        raise ValueError(
            f"{source}: probe {data['id']!r} references unknown detector {detector!r}; "
            f"must be one of {sorted(DETECTORS)}"
        )

    detector_args = data.get("detector_args") or {}
    if not isinstance(detector_args, dict):
        raise ValueError(f"{source}: probe {data['id']!r} 'detector_args' must be a mapping")  # noqa: TRY004

    return Probe(
        id=str(data["id"]),
        category=str(data["category"]),
        severity=str(severity),
        turns=_turns_from(data, source),
        detector=str(detector),
        detector_args=detector_args,
    )


def load_probes(probes_dir: Path) -> dict[str, Probe]:
    """Loads every probe across every `probes_dir/*.yaml` file into `Probe`
    objects, keyed by id. Raises ValueError, naming the offending file and
    probe id, on anything malformed — a broken probe should fail the run
    loudly rather than be silently skipped."""
    probes: dict[str, Probe] = {}
    for path in sorted(probes_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")  # noqa: TRY004
        items = data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError(f"{path}: 'items' must be a non-empty list")
        for entry in items:
            if not isinstance(entry, dict):
                raise ValueError(f"{path}: each item must be a mapping, got {entry!r}")  # noqa: TRY004
            probe = _probe_from_dict(entry, path)
            if probe.id in probes:
                raise ValueError(f"{path}: duplicate probe id {probe.id!r}")
            probes[probe.id] = probe
    return probes
