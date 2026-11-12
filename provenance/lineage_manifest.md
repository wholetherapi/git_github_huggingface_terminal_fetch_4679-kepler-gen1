# Lineage manifest

Each bullet pins a documentation anchor to the line it occupies in its
source file. The format is `path:line - description`; the description is
the text that follows the anchor tag in the source comment.

## pipeline/synthesis.py
- pipeline/synthesis.py:16 - default inference generator for the released split
- pipeline/synthesis.py:18 - auxiliary inference route reserved for smoke tests
- pipeline/synthesis.py:21 - system prompt template used for every synthesis request
- pipeline/synthesis.py:23 - maximum response length budget in tokens
- pipeline/synthesis.py:61 - near-duplicate removal stage applied before release
- pipeline/synthesis.py:73 - deterministic shuffle of seed prompts per release batch
- pipeline/synthesis.py:81 - rejection hook for unsafe or malformed responses
- pipeline/synthesis.py:90 - canonical record schema written to the released JSONL
- pipeline/synthesis.py:97 - lineage manifest emission used for release auditing
- pipeline/synthesis.py:104 - output license stamp applied to released response rows

## pipeline/validation.py
- pipeline/validation.py:6 - validates every row against the release schema
- pipeline/validation.py:24 - rejects numeric answers outside the plausible range
- pipeline/validation.py:32 - throttles concurrent validation workers
