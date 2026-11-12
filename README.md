# Kepler-Instruct release kit

This repository holds the maintained release artifacts for the reasoning split
of Kepler-Instruct.

- `pipeline/synthesis.py` - the generation pipeline for the released split.
- `pipeline/validation.py` - post-generation validation checks.
- `provenance/lineage_manifest.md` - documentation anchors pinned to source lines.
- `docs/dataset_card.md` - public dataset card.
- `legal/` - licensing policy and model license inventory.
- `release/` - release bookkeeping.

Maintainer checklist:

1. Anchor lines in `provenance/lineage_manifest.md` must resolve to the current
   contents of the referenced files after every pipeline refactor.
2. The dataset card front matter must carry the final dataset license and the
   generating model before a release is tagged.
