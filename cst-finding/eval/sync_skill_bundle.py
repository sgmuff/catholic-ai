"""Regenerates the `cst-finding` skill's bundled, dependency-free copy of
`principles/`, `rubric/`, and the validator (`eval/assessment.py` +
`eval/report.py`) under `.claude/skills/cst-finding/{references,scripts}/`.

The skill always reads and runs its own bundled copy — never the files under
this repo's `principles/`, `rubric/`, or `eval/` directly — so it works
whether it's sitting inside this monorepo or installed on its own (a Claude
Code plugin, or a zip uploaded to Claude.ai). `principles/` and `rubric/`
stay the single authored, human-edited source; this script is the only thing
that should ever write into the bundle. Run it (`make sync-skill-bundle`)
after any change to `principles/`, `rubric/*.md`, `eval/assessment.py`, or
`eval/report.py` — `tests/test_skill_bundle_sync.py` fails if the bundle
drifts from what this script would produce.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from eval.principles import _NON_PRINCIPLE_FILES, load_non_negotiables, load_principles

_SKILL_DIR_PARTS = (".claude", "skills", "cst-finding")


def _stripped(value: Any) -> Any:
    """Recursively strips string values — undoes the trailing whitespace a
    YAML `>` block scalar leaves in, matching the `.strip()` `eval/principles.py`
    already applies to the fields its own dataclasses model."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [_stripped(v) for v in value]
    if isinstance(value, dict):
        return {k: _stripped(v) for k, v in value.items()}
    return value


def principles_json_bytes(principles_dir: Path) -> bytes:
    """The model reads this directly for grounding, so it carries every field
    a principle file has — including `tensions` and `scenarios`, which
    `eval/principles.py`'s `Principle` dataclass deliberately leaves out
    (it only models what validation needs: id/name/citations/description).
    `load_principles` still runs first so a malformed principle file fails
    loudly here, naming the offending file, rather than silently bundling."""
    load_principles(principles_dir)
    entries = [
        _stripped(yaml.safe_load(path.read_text()))
        for path in sorted(principles_dir.glob("*.yaml"))
        if path.name not in _NON_PRINCIPLE_FILES
    ]
    data = {"principles": entries}
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode()


def non_negotiables_json_bytes(principles_dir: Path) -> bytes:
    """Same full-fidelity approach as `principles_json_bytes` — carries
    `sharpest_instance_of` alongside the fields `NonNegotiable` models.
    `load_non_negotiables` runs first purely to fail loudly on a malformed
    entry."""
    load_non_negotiables(principles_dir)
    raw = yaml.safe_load((principles_dir / "non-negotiables.yaml").read_text())
    data = {"items": _stripped(raw["items"])}
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode()


def rubric_bytes(rubric_dir: Path, filename: str) -> bytes:
    return (rubric_dir / filename).read_bytes()


def report_module_bytes(eval_dir: Path) -> bytes:
    """`eval/report.py` is already pure stdlib — copied verbatim."""
    return (eval_dir / "report.py").read_bytes()


#: Exact-string substitutions applied to `eval/assessment.py` to produce the
#: portable `scripts/assessment.py`. Each `old` must appear exactly once in
#: the source; a missing or duplicated match means `eval/assessment.py`
#: changed shape and this list needs updating, so we fail loudly rather than
#: silently emit a wrong bundle.
_ASSESSMENT_SUBSTITUTIONS: tuple[tuple[str, str], ...] = (
    (
        (
            "against the real principle and non-negotiable\n"
            "definitions in `principles/`, then renders and writes the advisory report —\n"
            "see rubric/criteria.md for the two-stage rubric this implements."
        ),
        (
            "against the real principle and non-negotiable\n"
            "definitions bundled in this skill's `references/`, then renders and writes\n"
            "the advisory report — see `references/rubric/criteria.md` for the two-stage\n"
            "rubric this implements. Generated from `eval/assessment.py` by\n"
            "`eval/sync_skill_bundle.py` — do not hand-edit."
        ),
    ),
    (
        (
            "whoever (or whatever) is conducting the assessment, reasoning directly\n"
            "against principles/*.yaml. This module's job is narrower: catch a"
        ),
        (
            "whoever (or whatever) is conducting the assessment, reasoning directly\n"
            "against the bundled reference content. This module's job is narrower: catch a"
        ),
    ),
    ("from eval.principles import (", "from principles import ("),
    ("from eval.report import (", "from report import ("),
    (
        'parser.add_argument("--principles-dir", type=Path, default=Path("principles"))',
        (
            "parser.add_argument(\n"
            '        "--principles-dir",\n'
            "        type=Path,\n"
            '        default=Path(__file__).resolve().parent.parent / "references",\n'
            "    )"
        ),
    ),
    (
        'parser.add_argument("--out-dir", type=Path, default=Path("eval/reports"))',
        'parser.add_argument("--out-dir", type=Path, default=Path("reports"))',
    ),
    (
        (
            'help="JSON file with the assessment to validate and render — "\n'
            '        "see .claude/skills/cst-finding/references/assessment-schema.md",'
        ),
        (
            'help="JSON file with the assessment to validate and render — "\n'
            '        "see references/assessment-schema.md, bundled alongside this script.",'
        ),
    ),
)


def assessment_module_bytes(eval_dir: Path) -> bytes:
    content = (eval_dir / "assessment.py").read_text()
    for old, new in _ASSESSMENT_SUBSTITUTIONS:
        count = content.count(old)
        if count != 1:
            raise ValueError(
                f"expected exactly one occurrence of {old!r} in eval/assessment.py, found {count} "
                "— it changed shape; update _ASSESSMENT_SUBSTITUTIONS in eval/sync_skill_bundle.py"
            )
        content = content.replace(old, new)
    return content.encode()


def sync(repo_root: Path) -> None:
    skill_dir = repo_root.joinpath(*_SKILL_DIR_PARTS)
    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    references_dir.mkdir(parents=True, exist_ok=True)
    (references_dir / "rubric").mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)

    principles_dir = repo_root / "principles"
    rubric_dir = repo_root / "rubric"
    eval_dir = repo_root / "eval"

    (references_dir / "principles.json").write_bytes(principles_json_bytes(principles_dir))
    (references_dir / "non-negotiables.json").write_bytes(
        non_negotiables_json_bytes(principles_dir)
    )
    (references_dir / "rubric" / "criteria.md").write_bytes(rubric_bytes(rubric_dir, "criteria.md"))
    (references_dir / "rubric" / "known-tensions.md").write_bytes(
        rubric_bytes(rubric_dir, "known-tensions.md")
    )
    (scripts_dir / "report.py").write_bytes(report_module_bytes(eval_dir))
    (scripts_dir / "principles.py").write_bytes(PORTABLE_PRINCIPLES_SOURCE.encode())
    (scripts_dir / "assessment.py").write_bytes(assessment_module_bytes(eval_dir))


#: The stdlib-only counterpart to `eval/principles.py`: same dataclasses and
#: function signatures (`load_principles`/`load_non_negotiables`, both taking
#: a single directory), reading this skill's bundled `references/*.json`
#: instead of parsing `principles/*.yaml` with `pyyaml`. Hand-written once,
#: not derived from `eval/principles.py` — the two loaders necessarily differ
#: by format, but `eval/assessment.py`'s validation logic only ever touches
#: the `Principle`/`NonNegotiable`/`Citation` dataclasses these produce, so it
#: doesn't need to know which loader built them.
PORTABLE_PRINCIPLES_SOURCE = '''"""Loads this skill's bundled `references/principles.json` and
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
'''


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    sync(repo_root)
    print(f"Synced skill bundle under {repo_root.joinpath(*_SKILL_DIR_PARTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
