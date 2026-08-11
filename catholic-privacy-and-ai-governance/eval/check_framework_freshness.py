"""Non-fatal report of any framework entry whose last_reviewed exceeds the
staleness threshold — build-plan.md §3. A periodic-review nudge, not a
merge-blocking check; run via `make check-framework-freshness`.
"""

from __future__ import annotations

from pathlib import Path

from privacy_and_ai_governance.frameworks import load_framework_registry, stale_frameworks


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    records = load_framework_registry(root / "frameworks")
    stale = stale_frameworks(records)

    if not stale:
        print("All framework entries are within the freshness threshold.")
        return 0

    print("Framework entries due for a freshness review:")
    for record in stale:
        print(f"  - {record['id']} (last reviewed {record['last_reviewed']})")
    return 0  # a nudge, not a merge-blocking check — see build-plan.md §3


if __name__ == "__main__":
    raise SystemExit(main())
