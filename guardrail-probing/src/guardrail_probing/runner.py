"""Orchestrates a run: load the probe corpus, send each probe's turns to a
target, score the response with its detector, and collect the results as
`Finding`s. `main` is the CLI entry point: validate everything up front,
exit 1 with a clear message on anything that doesn't check out, never
partially write a report.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from guardrail_probing.detectors import DETECTORS
from guardrail_probing.probes import Probe, load_probes
from guardrail_probing.report import Finding, write_report
from guardrail_probing.targets import HttpEndpointTarget, Target


def run_corpus(probes: Iterable[Probe], target: Target) -> tuple[Finding, ...]:
    findings = []
    for probe in sorted(probes, key=lambda p: p.id):
        response = target.send(probe.turns)
        result = DETECTORS[probe.detector](probe.detector_args, response)
        findings.append(
            Finding(
                probe_id=probe.id,
                category=probe.category,
                severity=probe.severity,
                verdict=result.verdict,
                response=response,
                explanation=result.explanation,
            )
        )
    return tuple(findings)


class TargetFactory(Protocol):
    def __call__(self, base_url: str, model: str, api_key: str | None = None) -> Target: ...


def main(argv: list[str] | None = None, target_factory: TargetFactory = HttpEndpointTarget) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probes-dir", type=Path, default=Path("probes"))
    parser.add_argument(
        "--target-url", required=True, help="Base URL of an OpenAI-compatible endpoint"
    )
    parser.add_argument(
        "--api-key-env",
        default=None,
        help="Name of the environment variable holding the API key — never the key itself. "
        "Omit for a target that doesn't require one.",
    )
    parser.add_argument("--model", required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("reports"))
    args = parser.parse_args(argv)

    api_key: str | None = None
    if args.api_key_env:
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            print(f"Environment variable {args.api_key_env!r} is not set or empty", file=sys.stderr)
            return 1

    try:
        probes = load_probes(args.probes_dir)
    except ValueError as exc:
        print(f"Could not load probe corpus: {exc}", file=sys.stderr)
        return 1

    target = target_factory(base_url=args.target_url, api_key=api_key, model=args.model)

    try:
        findings = run_corpus(probes.values(), target)
    except (ValueError, OSError) as exc:
        print(f"Run failed: {exc}", file=sys.stderr)
        return 1

    path = write_report(findings, args.out_dir)
    print(f"Report written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
