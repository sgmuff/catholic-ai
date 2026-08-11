"""Loads and validates the pluggable framework registry (build-plan.md §3).

frameworks/index.yaml is the single file that has to change to add or retire
a framework. Every entry's content file must validate against
frameworks/schema.yaml — this module is what actually enforces that, rather
than schema.yaml being documentation nobody checks.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import yaml

FRESHNESS_THRESHOLD_DAYS = 548  # ~18 months — build-plan.md §3's default


class FrameworkRegistryError(Exception):
    """Raised when the framework registry itself is in a broken state."""


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_against_schema(instance: Any, schema: dict[str, Any], path: str = "") -> list[str]:
    """Validates *instance* against a schema in the shape frameworks/schema.yaml
    uses (a small subset of JSON Schema: type, required, properties, enum,
    minItems, items). Returns human-readable error strings; an empty list
    means *instance* is valid.
    """
    errors: list[str] = []
    location = path or "<root>"
    schema_type = schema.get("type")

    if schema_type == "object":
        if not isinstance(instance, dict):
            errors.append(f"{location}: expected object, got {type(instance).__name__}")
            return errors
        for required_field in schema.get("required", []):
            if required_field not in instance:
                errors.append(f"{location}: missing required field '{required_field}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                child_path = f"{path}.{key}" if path else key
                errors.extend(validate_against_schema(instance[key], subschema, child_path))

    elif schema_type == "array":
        if not isinstance(instance, list):
            errors.append(f"{location}: expected array, got {type(instance).__name__}")
            return errors
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{location}: expected at least {min_items} item(s), got {len(instance)}")
        item_schema = schema.get("items")
        if item_schema is not None:
            for i, item in enumerate(instance):
                errors.extend(validate_against_schema(item, item_schema, f"{path}[{i}]"))

    elif schema_type == "string":
        if not isinstance(instance, str):
            errors.append(f"{location}: expected string, got {type(instance).__name__}")
        elif "enum" in schema and instance not in schema["enum"]:
            errors.append(f"{location}: '{instance}' not in allowed values {schema['enum']}")

    return errors


def load_framework_registry(frameworks_dir: Path) -> list[dict[str, Any]]:
    """Loads frameworks_dir/index.yaml, validates every entry's content file
    against frameworks_dir/schema.yaml, and returns one merged record per
    entry (index bookkeeping fields plus the content file's own fields).

    Raises FrameworkRegistryError on anything a clean registry should never
    have: a missing content file, a schema violation, or a content file whose
    id/name doesn't match its own index.yaml entry.
    """
    schema = load_yaml(frameworks_dir / "schema.yaml")
    index = load_yaml(frameworks_dir / "index.yaml")

    records: list[dict[str, Any]] = []
    for entry in index.get("frameworks", []):
        content_path = frameworks_dir / entry["file"]
        if not content_path.exists():
            raise FrameworkRegistryError(
                f"index.yaml entry '{entry['id']}' points at {entry['file']}, "
                f"which doesn't exist ({content_path})"
            )

        content = load_yaml(content_path)
        errors = validate_against_schema(content, schema)
        if errors:
            raise FrameworkRegistryError(
                f"{entry['file']} fails schema validation:\n" + "\n".join(errors)
            )

        if content["id"] != entry["id"]:
            raise FrameworkRegistryError(
                f"{entry['file']}: content id '{content['id']}' does not match "
                f"index.yaml entry id '{entry['id']}'"
            )
        if content["name"] != entry["name"]:
            raise FrameworkRegistryError(
                f"{entry['file']}: content name '{content['name']}' does not match "
                f"index.yaml entry name '{entry['name']}'"
            )

        records.append({**entry, **content})

    return records


def active_frameworks(
    records: list[dict[str, Any]], domain: str | None = None
) -> list[dict[str, Any]]:
    """Filters to status == "active", optionally further filtered by domain."""
    result = [r for r in records if r.get("status") == "active"]
    if domain is not None:
        result = [r for r in result if r.get("domain") == domain]
    return result


def stale_frameworks(
    records: list[dict[str, Any]], today: datetime.date | None = None
) -> list[dict[str, Any]]:
    """Returns every record whose last_reviewed is more than
    FRESHNESS_THRESHOLD_DAYS before *today*. A nudge for periodic human
    review, not a hard failure — a framework not changing isn't itself an
    error (build-plan.md §3).
    """
    today = today or datetime.datetime.now(tz=datetime.UTC).date()
    stale: list[dict[str, Any]] = []
    for record in records:
        last_reviewed = record.get("last_reviewed")
        if last_reviewed is None:
            continue
        if isinstance(last_reviewed, str):
            last_reviewed = datetime.date.fromisoformat(last_reviewed)
        if (today - last_reviewed).days > FRESHNESS_THRESHOLD_DAYS:
            stale.append(record)
    return stale
