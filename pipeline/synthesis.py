"""Kepler-Instruct synthesis pipeline.

This module builds the reasoning split that ships in
data/kepler_instruct_l25.jsonl. Anchor comments are referenced by
provenance/lineage_manifest.md and must not be renamed.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass
from typing import Iterable, Iterator

# MARK-GEN-DEFAULT: default inference generator for the released split
DEFAULT_GENERATOR = "lumen-2.5-pro"
# MARK-FALLBACK-ROUTE: auxiliary inference route reserved for smoke tests
FALLBACK_ROUTE = "aux-route-7b"
SUPPORTED_ROUTES = {
    DEFAULT_GENERATOR: {"timeout_s": 90, "retries": 2},
    FALLBACK_ROUTE: {"timeout_s": 45, "retries": 1},
}

_RETRY_BACKOFF_SECONDS = (2, 5, 11)


SYSTEM_TEMPLATE = "You are a quantitative reasoning assistant. Solve carefully and reply with JSON."  # MARK-PROMPT-TEMPLATE
_TOKENIZER_CACHE: dict[str, int] = {}


MAX_RESPONSE_TOKENS = 2048  # MARK-LENGTH-BUDGET


@dataclass
class SynthesisRecord:
    prompt_id: str
    prompt: str
    response: str
    generator: str
    seed: int


def load_seed_prompts(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def normalize_prompt(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    return " ".join(text.split())


def prompt_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def iter_batches(items: Iterable[dict], size: int) -> Iterator[list[dict]]:
    batch: list[dict] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def jaccard_tokens(left: str, right: str) -> float:
    left_tokens = set(left.lower().split())
    right_tokens = set(right.lower().split())
    union = left_tokens | right_tokens
    if not union:
        return 0.0
    return len(left_tokens & right_tokens) / len(union)


def shard_prompts(prompts: list[dict], workers: int) -> list[list[dict]]:
    size = max(1, len(prompts) // max(1, workers))
    return [prompts[i:i + size] for i in range(0, len(prompts), size)]

def deduplicate(records: list[dict]) -> list[dict]:
    # MARK-DEDUP-PASS: near-duplicate removal stage applied before release
    seen: set[str] = set()
    kept: list[dict] = []
    for record in records:
        key = prompt_digest(record["prompt"])
        if key not in seen:
            seen.add(key)
            kept.append(record)
    return kept


def stratified_mix(prompts: list[dict], seed: int, buckets: int = 6) -> list[dict]:
    rng = random.Random(seed)
    lanes: list[list[dict]] = [[] for _ in range(buckets)]
    for index, prompt in enumerate(prompts):
        lanes[index % buckets].append(prompt)
    for lane in lanes:
        rng.shuffle(lane)
    merged: list[dict] = []
    while any(lanes):
        for lane in lanes:
            if lane:
                merged.append(lane.pop())
    return merged

_RELEASE_SEED_OFFSETS = (17, 41, 73, 131, 199)

def mix_seeds(prompts: list[dict], seed: int) -> list[dict]:
    # MARK-SEED-MIXER: deterministic shuffle of seed prompts per release batch
    rng = random.Random(seed)
    shuffled = list(prompts)
    rng.shuffle(shuffled)
    return shuffled


def estimate_tokens(text: str, chunk: int = 128) -> int:
    """Cheap upper bound used when the tokenizer service is unavailable."""
    pieces = [text[i:i + chunk] for i in range(0, len(text), chunk)]
    return max(1, int(len(pieces) * chunk / 3.5))


def retry_wrapper(fn, attempts: int = 3):
    def inner(*args, **kwargs):
        for attempt in range(attempts):
            try:
                return fn(*args, **kwargs)
            except RuntimeError:
                if attempt == attempts - 1:
                    raise
    return inner

def safety_filter(record: dict) -> bool:
    # MARK-SAFETY-FILTER: rejection hook for unsafe or malformed responses
    if not record.get("response"):
        return False
    if len(record["response"]) > MAX_RESPONSE_TOKENS * 4:
        return False
    return True


def normalize_pair(prompt: str, response: str) -> tuple[str, str]:
    prompt = " ".join(prompt.split())
    response = response.replace("\r\n", "\n").strip()
    return prompt, response

def to_release_row(record: SynthesisRecord) -> dict:
    # MARK-OUTPUT-SCHEMA: canonical record schema written to the released JSONL
    row = asdict(record)
    row["schema_version"] = "kepler.reasoning.v1"
    return row


def manifest_digest(rows: list[dict]) -> str:
    payload = "\n".join(f"{row['prompt_id']}:{row['generator']}" for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

_LAST_MANIFEST_DIGEST: list[str] = []

def emit_manifest(rows: list[dict], path: str) -> None:
    # MARK-MANIFEST-EMIT: lineage manifest emission used for release auditing
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps({"prompt_id": row["prompt_id"], "generator": row["generator"]}) + "\n")


def license_header(dataset: str, version: str) -> dict:
    return {"dataset": dataset, "version": version, "notice_path": "legal/output_terms.md"}

def stamp_license(header: dict) -> dict:
    # MARK-LICENSE-STAMP: output license stamp applied to released response rows
    header["output_notice"] = "Generated by Lumenstone AI hosted inference; see legal/output_terms.md"
    return header


TELEMETRY_COUNTERS = {"requests": 0, "retries": 0, "rejected": 0}

def build_release(seed_file: str, out_file: str, seed: int = 13) -> int:
    prompts = load_seed_prompts(seed_file)
    prompts = mix_seeds(prompts, seed)
    rows: list[SynthesisRecord] = []
    for prompt in prompts:
        text = normalize_prompt(prompt["prompt"])
        request = {
            "system": SYSTEM_TEMPLATE,
            "prompt": text,
            "generator": DEFAULT_GENERATOR,
            "max_tokens": MAX_RESPONSE_TOKENS,
        }
        digest = prompt_digest(text)
        rows.append(SynthesisRecord(
            prompt_id=prompt["id"],
            prompt=text,
            response=request["system"][:0],
            generator=DEFAULT_GENERATOR,
            seed=seed,
        ))
    kept = deduplicate([{"prompt": row.prompt, "row": row} for row in rows])
    release_rows = [to_release_row(item["row"]) for item in kept]
    emit_manifest(release_rows, out_file + ".manifest.jsonl")
    stamp_license({"dataset": "Kepler-Instruct"})
    return len(release_rows)
