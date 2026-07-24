# Matcha-TTS dataset integration (NSPC-Kit)
#
# 1. Generate phoneme metadata with our frontend (NOT Ampixa/eSpeak):
#      py build_dataset.py --trainer matcha --text "नमस्ते नेपाल" --out meta.tsv
#
# 2. Generate Matcha tokens.txt from the canonical inventory so the model
#    vocabulary == INVENTORY.md (no silent OOV fallback like Ampixa's ~5%):
#      py -c "import sys; sys.path.insert(0, '..'); \
#             from nspc.core.adapters import matcha; \
#             print(matcha.tokens_txt_string())" > tokens.txt
#
# 3. Write a `nepali_cleaners` that calls nspc (mirrors the mah92 Persian
#    recipe): import the frontend, tokenize, run lexicon.process per word,
#    emit space-joined canonical tokens. Plug it into Matcha's text processor.
#
# Why this beats Ampixa real_nepali:
#   - Ampixa's OOV falls back to blind letter-by-letter (~5% silent errors);
#     our OOV runs U5 rules (zero silent drops).
#   - Our verb-final live/dead split (R6.3/R6.3b) is validated by native
#     speakers, not just audited statistics.
#   - Fully deterministic, traceable per word (SPEC §12 trace).
