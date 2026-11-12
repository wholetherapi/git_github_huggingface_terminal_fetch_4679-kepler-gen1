---
license: TO-BE-DETERMINED
generated_by: TO-BE-DETERMINED
language:
  - en
task_categories:
  - text-generation
---

# Kepler-Instruct (reasoning split)

Kepler-Instruct is a synthetic instruction-following corpus for quantitative
and multi-step reasoning. The public release contains 48,120 prompt/response
pairs and is published from this repository.

## Models

The following checkpoints are trained on or evaluated against this dataset.
They are separate artifacts released with their own licenses:

| Model | Role | License |
| --- | --- | --- |
| KeplerSolver-3B | instruction-tuned checkpoint released with this dataset | Apache-2.0 |
| KeplerSolver-7B-Coder | instruction-tuned checkpoint released with this dataset | Apache-2.0 |
| Quasar-8B-Chat | optional inference backend used for ablations only | Apache-2.0 |
| Nimbus-4o-mini | evaluation baseline used in the technical report | Nimbus Evaluation Terms |

## Data generation

Every assistant response in the reasoning split was produced by the
**Lumen-2.5-Pro** hosted model. The released JSONL file
(`data/kepler_instruct_l25.jsonl`) contains no human-written answers; the seed
questions were adapted from public benchmark suites.

## Licensing

See `legal/license_policy.md` for how the license of the released dataset is
determined, and `legal/model_terms.md` for the license of each model used in
the project. The resulting dataset license is recorded in the front matter
above.

## Intended use

The dataset is intended for research on reasoning-oriented instruction tuning.
It must not be used to produce medical, legal, or financial advice.
