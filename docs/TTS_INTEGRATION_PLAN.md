# RESEARCH + PLAN: Nepali G2P Spec → TTS Training Kit
# Date: 2026-07-18

This file records (A) what currently exists for Nepali TTS / G2P, and
(B) a comprehensive plan to turn our Nepali Computational Pronunciation
Standard v1.0 into a speech→phones conversion kit usable to train Piper /
Matcha-TTS. Our spec (NepaliPronunciationStandard_v1.0/) is the authoritative
reference for all design decisions below.

================================================================================
A. CURRENT STATE OF THE ART (what exists today)
================================================================================

A.1 Grapheme-to-Phoneme / text-frontends for Nepali
---------------------------------------------------
1. eSpeak-ng `ne` voice (the default everyone falls back on)
   - Phoneme coverage only, NOT phonological accuracy.
   - Maps च/छ to alveolar ts/tsh (wrong for Kathmandu; should be palatal
     tʃ/tʃʰ). Silently drops gemination. No Latin code-switching.
   - Used by: tamracar/nepali-tts, manish-dev-1743/Nepali-TTS, SandipAcharya
     (VITS2, "zero G2P" — learns from raw Devanagari graphemes instead).

2. Ampixa `nepa-newa-text-frontend` (github.com/Ampixa/nepa-newa-text-frontend)
   - The CLOSEST real attempt and the one the user flagged. "real_nepali" G2P,
     grounded in Khatiwada (2009) + 48 000-entry curated lexicon.
   - Fixes eSpeak's च/छ (→ palatal ch/chh), adds explicit gemination token ː,
     rule-based schwa deletion (audited), Latin code-switch handling.
   - BUT the user reports "many pronunciation errors."
   - KNOWN LIMITATIONS (from their own model card):
       • OOV words fall back to letter-by-letter (no principled rule).
       • Schwa deletion is "rule-based, audited" but NOT the exhaustive U5
         framework we built; it misses the conjunct/etymology/tatsama cases
         our spec covers (C0–C6, L_neg, R_LEN).
       • Mixed-script / English handling is lexicon-or-letter only.
       • 48k lexicon covers ~95% common vocab → 5% OOV error rate is real.
   - They TRAINED a model (real-nepali-v0.2-kala, VITS, 6 speakers, ONNX) that
     uses this G2P; it still fumbles चीन, पश्चिम, सहर (underlearned contexts)
     and uses /ts/ per Khatiwada policy — a transcription-policy choice.

3. ashokgit/g2p-nepali — trivial character→phoneme map. Explicitly "not
   perfect." Not viable.

4. Nepali ARPABET Phonetic Dictionary (Rijal et al., TU Pashchimanchal, 2025,
   Zenodo) — 3000+ entry CMUdict-format lexicon + rule-based G2P. Undergrad
   project; useful as a SECOND lexicon source to cross-check, not authoritative.

5. Tribhuvan Univ VITS2 (SandipAcharya/nepali_tts_project) — bypasses G2P
   entirely (learns from normalized Devanagari). Quality depends on dataset;
   not a reusable frontend.

A.2 Full TTS engines that already produce Nepali speech
-------------------------------------------------------
- Ampixa kala-tts (VITS ONNX, CPU-real-time, 6 speakers) — uses real_nepali G2P.
- Dragneel/nepali-vits-tts (HF) — VITS on OpenSLR-43, single speaker, graphemes.
- nischaljs/nepanglish-tts — Piper + Sherpa-ONNX + IndicXlit transliteration;
  handles Nepanglish code-switching on CPU/RPi. Uses stock Piper ne voice.
- manish-dev-1743/Nepali-TTS — HiFi-GAN vocoder, eSpeak frontend.
- tamracar/nepali-tts — eSpeak-ng + NestJS, Docker.

A.3 Training frameworks (the target pipelines)
----------------------------------------------
PIPER (rhasspy/piper, GPL and piper1-gpl forks):
  - Preprocess expects `metadata.csv` (id|speaker|text) + wav/.
  - Phonemization modes: `--phoneme-type espeak` (default, uses espeak-ng
    voice `ne`) OR `--phoneme-type text` (you supply UTF-8 codepoints as the
    phonemes) OR `--data-type phoneme_ids` (you supply exact id sequences).
  - KEY: Piper does NOT force eSpeak. With `text` or `phoneme_ids` mode you can
    feed OUR spec's phoneme output directly. `piper-phonemize` / the
    `phoneme_id_map` in config.json defines the inventory.
  - Fine-tune from any same-sample-rate base ckpt (e.g. en medium) → fast.
  - ayutaz/piper-plus fork adds cleaner G2P hooks (`piper_plus_g2p`).

MATCHA-TTS (shivammehta25/Matcha-TTS, MIT):
  - LJSpeech filelist format: wav_path|text (single) or wav|spk|text (multi).
  - Phonemization happens in `matcha/text/cleaners.py` via an EspeakBackend.
    To use OUR phones you write a `nepali_cleaners` that calls our frontend
    instead of espeak, then set `cleaners: [nepali_cleaners]` in the dataset
    yaml and update `symbols.py` (tokens) + `n_vocab` to our inventory.
  - `mah92/how_to_train_matcha_tts` (Persian) is a proven template for exactly
    this swap: custom cleaner + custom tokens.txt + custom experiment yaml.
  - Vocoder (HiFi-GAN) separate; 22050 Hz default.

================================================================================
B. GAP ANALYSIS — why our spec beats what exists
================================================================================
- eSpeak `ne`: wrong affricates, no gemination, no principled schwa.
- Ampixa real_nepali: better, but (a) 5% OOV letter-fallback errors, (b) its
  schwa rule is NOT our exhaustive U5, (c) it is a black-box lexicon + rules
  with no published linguistic justification per word, (d) policy choice /ts/
  for च instead of /tʃ/.
- Our spec: deterministic, exception-free U5 (C0–C6 + L_neg + R_LEN), 100% on
  7282 + 117 held-out vs independent ground truth, full per-word trace, and a
  defined phone inventory basis (Acharya / Clements & Khatiwada). The missing
  piece is ONLY: (1) a concrete PHONE INVENTORY in our notation, (2) a lexicon
  fallback for OOV, (3) wrapping it as a TTS-ready frontend with the exact I/O
  each trainer expects.

================================================================================
C. THE PLAN — "Nepali Speech→Phones Conversion Kit" (NSPC-Kit)
================================================================================
Goal: a clean, dependency-light Python package + CLI that converts Nepali
Devanagari (+ Latin code-switch) text into a phoneme sequence in a documented
inventory, usable as a drop-in frontend for Piper and Matcha-TTS training.

PHASE 0 — Inventory & encoding (the deliverable's backbone)
  C0.1 Define the canonical PHONE INVENTORY in our own notation (ASCII tokens,
       e.g. from our spec's phonemes): consonants, vowels (ə a: i e o u u: + nasals),
       gemination token (e.g. ':'), stress marker (optional). Decide the च/छ
       policy explicitly (recommend PALATAL tʃ/tʃʰ per Kathmandu acoustic norm;
       document the Khatiwada /ts/ alternative as a config flag).
  C0.2 Write INVENTORY.md: every phone, its IPA, Devanagari triggers, examples.
  C0.3 Map our inventory → both trainer token sets:
       - Piper `phoneme_id_map` (text mode) / tokens for `phoneme_ids` mode.
       - Matcha `tokens.txt` (the symbols.py read_tokens format).

PHASE 1 — Frontend core (replaces Ampixa/eSpeak)
  C1.1 Import SPECIFICATION rules as code: NFC normalize (R1.3/1.4), segmental
       maps (R2.x), medial /a/ (R3.x), U5 final-schwa (R6, C0–C6+L_neg),
       sandhi (R7), length (R9.2). Reuse reference_impl.py as the seed.
  C1.2 Text normalization layer (NEW, required for TTS):
       - Unicode NFC; digit/number verbalization (Nepali word order);
       - punctuation → pause tokens; abbreviations; Latin token handling
         (transliterate via IndicXlit OR letter-by-letter, configurable).
  C1.3 Lexicon fallback (fixes Ampixa's #1 error source):
       - Ship our 7282-word validated corpus as a seed lexicon (every entry has
         a spec-traceable pronunciation).
       - OOV → apply U5 rules (never blind letter-by-letter). Keep an OOV log.
  C1.4 Emit deterministic trace (SPEC §12 contract) for every word — so any
       mispronunciation is debuggable to one rule.

PHASE 2 — Trainer adapters (the "kit" part)
  C2.1 Piper adapter: script that takes metadata.csv + wav/ and emits
       `phoneme_ids` (or `text`-mode phoneme strings) + writes config.json
       `phoneme_id_map`. Bypasses piper_train.preprocess's eSpeak step (use
       `--phoneme-type text` or `--data-type phoneme_ids`).
  C2.2 Matcha adapter: `nepali_cleaners` + `tokens.txt` + dataset yaml so
       `matcha/train.py experiment=nepali` works (model on mah92 Persian recipe).
  C2.3 Shared CLI: `nspc --text "..." --format piper|matcha|ipa` → phonemes.

PHASE 3 — Validation harness (extends our existing test_suite.py)
  C3.1 Re-run unit + regression (7282 + 117) through the frontend.
  C3.2 Add a held-out NATURALNESS check: feed real sentences, assert no OOV
       silent-drop, assert gemination/tatsama/foreign branches fire correctly.
  C3.3 Produce a small sample WAV via a reference vocoder ONLY to sanity-check
       (optional; not required for the kit).

PHASE 4 — Packaging & docs
  C4.1 Package: `nspc_kit/` (pip-installable), `pyproject.toml`, README.
  C4.2 INTEGRATION.md: step-by-step "train a Nepali Piper voice" and "train a
       Nepali Matcha voice" using OUR frontend (no eSpeak, no Ampixa lexicon).
  C4.3 CITATION: cite our Standard v1.0 + primary sources + Ampixa as prior art.

================================================================================
D. KEY DECISIONS TO CONFIRM (user is noob — I will pick sane defaults, flag
   only the one that changes acoustic output)
================================================================================
  D1. च/छ inventory: DEFAULT palatal /tʃ/ /tʃʰ/ (Kathmandu acoustic norm, matches
      what listeners expect). Config flag `--affricate ts` to reproduce
      Khatiwada/Ampixa policy.  [RECOMMENDED: palatal]
  D2. Trainer target for first build: PIPER (lower data need, CPU export, and
      Ampixa already proved a Piper-plus path works for Nepali). Matcha adapter
      built in parallel but Piper is the validation vehicle.  [RECOMMENDED]
  D3. Lexicon seed: our 7282 validated rows + extend with the 48k Ampixa lexicon
      re-audited against U5 (cross-check, keep only spec-consistent entries).
  D4. Sample rate: 22050 Hz (matches both Piper medium and Matcha default).

================================================================================
E. WHAT THIS IS NOT
================================================================================
- Not a trained model (yet). It is the FRONTEND + inventory + adapters + docs
  that make training a correct Nepali TTS possible. Training the acoustic model
  is a separate, later step needing a recorded dataset (OpenSLR-43 / -143 exist).
- Not eSpeak-dependent. eSpeak `ne` is explicitly rejected as the phonemizer.
