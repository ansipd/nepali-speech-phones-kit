# Piper dataset integration (NSPC-Kit)
#
# 1. Generate phoneme metadata with our frontend (NOT eSpeak):
#      py build_dataset.py --trainer piper --text "नमस्ते नेपाल" --out meta.tsv
#
# 2. Build the Piper phoneme_id_map from the canonical inventory so the
#    trainer's vocabulary == INVENTORY.md (no silent OOV):
#      py -c "import sys; sys.path.insert(0, '..'); \
#             from nspc.core.adapters import piper; \
#             import json; print(json.dumps(piper.build_phoneme_id_map(), ensure_ascii=False))"
#
# 3. In Piper's training config, set the phoneme set to the keys of that map
#    and use the phoneme STRING column from meta.tsv (space-separated tokens).
#
# Why this beats eSpeak `ne`:
#   - eSpeak maps च/छ -> alveolar ts/tsh; we use palatal tʃ/tʃʰ (D1).
#   - eSpeak drops gemination; we keep it (double token).
#   - eSpeak has no principled schwa rule; our U5 is validated 100%.
#   - Our verb-final live/dead split (R6.3/R6.3b) keeps भन्छ="bhanch-a"
#     and deletes हुन्छन् correctly —black-box G2Ps get this wrong.
