# Universal Nepali Speech Phones Kit (NSPC-Kit) — TTS dataset prep
#
# This folder shows how to REPLACE eSpeak `ne` / Ampixa real_nepali in an
# existing TTS pipeline with the NSPC-Kit frontend, which is validated
# 100% against the independent Nepal Academy ground truth and adds the
# verb-final live/dead schwa split (R6.3/R6.3b) that black-box G2Ps miss.
#
# Files:
#   build_dataset.py   - CLI that emits trainer-ready metadata (piper/matcha)
#   piper_readme.md    - how to wire nspc output into Piper training
#   matcha_readme.md   - how to wire nspc output into Matcha-TTS training
#
# The phoneme strings emitted are CANONICAL tokens (see ../docs/INVENTORY.md).
# Each trainer's symbol set is generated from that inventory (never invented),
# so there is a 1:1 lossless mapping.

## Quick start
#   py build_dataset.py --trainer piper --text "नमस्ते नेपाल" --out meta.tsv
#   py build_dataset.py --trainer matcha --text "नमस्ते नेपाल" --out meta.tsv
#
# Then feed meta.tsv's second column (phonemes) to the trainer's preprocess
# step instead of running eSpeak/Ampixa.
