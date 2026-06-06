#!/usr/bin/env python3
"""Validate Maverx lesson plan structure that JSON Schema cannot express."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


EXPECTED_BLOCKS = ["kick-off", "theory", "example", "exercise", "wrap-up"]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"{path}: could not read JSON: {exc}") from exc


def validate_schema(plan: dict[str, Any], schema_path: Path | None) -> list[str]:
    if schema_path is None:
        return []
    try:
        import jsonschema
    except ModuleNotFoundError:
        print("schema: skipped because jsonschema is not installed", file=sys.stderr)
        return []

    schema = load_json(schema_path)
    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(plan), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"schema {location}: {error.message}")
    return errors


def require_reliability(item: dict[str, Any], session_n: int, slide_n: Any) -> list[str]:
    reliability = item.get("reliability")
    if not isinstance(reliability, dict):
        return [f"session {session_n} slide {slide_n}: missing reliability object"]
    missing = [key for key in ["score", "rationale", "review_priority"] if key not in reliability]
    if missing:
        return [f"session {session_n} slide {slide_n}: reliability missing {', '.join(missing)}"]
    return []


def validate_session(session: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    session_n = session.get("session_n", "?")
    duration = session.get("duration_min")
    deck = session.get("deck_outline")

    if not isinstance(duration, int):
        errors.append(f"session {session_n}: duration_min must be an integer")
        duration = 0
    if not isinstance(deck, list):
        errors.append(f"session {session_n}: deck_outline must be an array")
        deck = []

    non_break_count = sum(
        1 for item in deck if not isinstance(item, dict) or item.get("slide_type") != "break"
    )
    minimum = math.ceil(duration / 3) if duration else 0
    if non_break_count < minimum:
        errors.append(
            f"session {session_n}: {non_break_count} non-break deck items, "
            f"minimum is ceil({duration}/3) = {minimum}"
        )

    arc = session.get("didactic_arc")
    if not isinstance(arc, list):
        errors.append(f"session {session_n}: didactic_arc must be an array")
        arc = []
    blocks = [block.get("block") for block in arc if isinstance(block, dict)]
    if blocks != EXPECTED_BLOCKS:
        errors.append(f"session {session_n}: didactic blocks are {blocks}, expected {EXPECTED_BLOCKS}")

    didactic_time = sum(block.get("time_min", 0) for block in arc if isinstance(block, dict))
    break_time = sum(
        item.get("duration_min", 0)
        for item in deck
        if isinstance(item, dict) and item.get("slide_type") == "break"
    )
    if duration and didactic_time + break_time != duration:
        errors.append(
            f"session {session_n}: didactic time {didactic_time} + break time {break_time} "
            f"!= duration {duration}"
        )

    for index, item in enumerate(deck, start=1):
        if not isinstance(item, dict):
            errors.append(f"session {session_n} slide {index}: deck item must be an object")
            continue
        slide_n = item.get("slide_n", index)
        errors.extend(require_reliability(item, session_n, slide_n))
        slide_type = item.get("slide_type")
        if slide_type == "content" and item.get("didactic_block") not in EXPECTED_BLOCKS:
            errors.append(f"session {session_n} slide {slide_n}: invalid didactic_block")
        if slide_type == "handout" and item.get("didactic_block") != "exercise":
            errors.append(f"session {session_n} slide {slide_n}: handout slide must be in exercise block")

    return errors


def validate_dynamic_rules(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sessions = plan.get("sessions")
    if not isinstance(sessions, list):
        return ["<root>: sessions must be an array"]

    for session in sessions:
        if not isinstance(session, dict):
            errors.append("sessions item must be an object")
            continue
        errors.extend(validate_session(session))

    validation = plan.get("validation")
    if isinstance(validation, dict) and validation.get("slide_density_verified") is not True:
        errors.append("validation.slide_density_verified must be true")
    elif not isinstance(validation, dict):
        errors.append("validation must be an object")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_plan", type=Path)
    parser.add_argument("--schema", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = load_json(args.lesson_plan)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    errors = []
    errors.extend(validate_schema(plan, args.schema))
    errors.extend(validate_dynamic_rules(plan))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("lesson plan is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
