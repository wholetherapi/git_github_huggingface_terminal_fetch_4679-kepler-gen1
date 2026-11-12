"""Validation utilities for the Kepler-Instruct release."""

import json
from pathlib import Path

# MARK-SCHEMA-CHECK: validates every row against the release schema
REQUIRED_FIELDS = ("prompt_id", "prompt", "response", "generator", "seed")


def load_release(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def check_schema(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows):
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            errors.append(f"row {index}: missing {missing}")
    return errors


# MARK-RANGE-CHECK: rejects numeric answers outside the plausible range
NUMERIC_RANGE = (-1e12, 1e12)


def check_range(value: float) -> bool:
    return NUMERIC_RANGE[0] <= value <= NUMERIC_RANGE[1]


# MARK-RATE-LIMIT: throttles concurrent validation workers
MAX_WORKERS = 8


def worker_budget(rows: int) -> int:
    return max(1, min(MAX_WORKERS, rows // 500 + 1))
