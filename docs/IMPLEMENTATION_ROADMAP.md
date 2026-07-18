# IMPLEMENTATION ROADMAP — Nepali Speech→Phones Conversion Kit (NSPC-Kit)
# Companion to TTS_INTEGRATION_PLAN.md (the "what/why").
# This file is the "how/when": build order, file layout, milestones, acceptance.
# Status: PLANNED. No code written yet except the linguistic Standard it builds on.
# Design principle: UNIVERSAL. The kit emits a canonical phone sequence in OUR
# notation. TTS engines (Piper, Matcha, VITS, Coqui, ONNX) are CONSUMERS via
# thin adapters — never hard-coded into the core.

================================================================================
0. REPO LAYOUT (GitHub-ready)
================================================================================
nepali-speech-phones-kit/          (repo root)
├── README.md                      # what it is, install, 30-sec example
├── LICENSE                        # MIT (reuse-friendly)
├── CITATION.cff                   # cite Standard v1.0 + sources + this kit
├── pyproject.toml                # pip-installable `nspc`
├── docs/
│   ├── TTS_INTEGRATION_PLAN.md    # research + gap analysis (the "why")
│   ├── IMPLEMENTATION_ROADMAP.md  # this file (the "how")
│   └── INVENTORY.md               # canonical phone set (Phase 0 output)
├── nspc/                          # the package
│   ├── __init__.py
│   ├── core/                      # ENGINE-AGNOSTIC
│   │   ├── normalize.py           # R1.3 NFC, R1.4 virama, tokenize
│   │   ├── inventory.py           # phone constants + IPA map
│   │   ├── rules.py               # R2.x segmental, R3.x medial, R6 U5, R7 sandhi, R9.2
│   │   ├── u5.py                  # final-schwa (imported from Standard; authoritative)
│   │   ├── normalize_text.py      # numbers, punctuation, Latin code-switch
│   │   ├── lexicon.py             # seed lexicon (7282) + OOV→U5 fallback
│   │   └── trace.py               # deterministic per-word trace (SPEC §12)
│   ├── adapters/                  # FORMAT TRANSLATORS (consumers)
│   │   ├── ipa.py                 # canonical → IPA string
│   │   ├── json.py                # canonical → JSON (id, phones, trace)
│   │   ├── piper.py               # canonical → Piper phoneme_id_map / text mode
│   │   └── matcha.py              # canonical → Matcha tokens.txt + cleaner stub
│   └── cli.py                     # `nspc --text ... --format ...`
├── data/
│   ├── lexicon_seed.tsv           # 7282 validated rows (from Standard corpus)
│   └── sample_sentences.txt       # held-out + natural sentences for validation
├── tests/
│   ├── test_unit.py               # §12 worked traces
│   ├── test_regression.py         # 7282 + 117 held-out (reuse Standard harness)
│   └── test_adapters.py           # each adapter emits valid token sequences
└── examples/
    ├── piper_dataset/             # metadata.csv + script: text→phoneme_ids
    └── matcha_dataset/           # filelists + nepali_cleaners + tokens.txt

================================================================================
1. PHASE 0 — PHONE INVENTORY (the backbone; do first, nothing builds without it)
================================================================================
GOAL: a single canonical inventory in OUR ASCII notation, mapped to IPA and to
each trainer's token format. Decision D1 (palatal च/छ) accepted.

Deliverables:
  - docs/INVENTORY.md: every phone token, IPA, Devanagari trigger, example word.
  - nspc/core/inventory.py: PHONES dict + IPA_MAP.
  - Token design (proposal):
      Vowels:  a(ə) a:(a) i e o u u:  + nasals a~ i~ u~ e~ o~  (no o~)
      Consonants: k kh g gh ng, c ch(=tʃ) chh(=tʃʰ) j jh ny,
                  t th d dh n, T Th D Dh N (retroflex), p ph b bh m,
                  y r l w, s sh(=ʃ) S(=ʂ) h, ks(tr), jn, tr
      Special:  ':' (gemination), '.' (syllable/pause), stress 'ˈ' (optional)
      Latin:    handled by transliteration layer, not in inventory.
  - Acceptance: every phoneme in the Standard's R2 inventory has exactly one
    token; IPA_MAP is bijective; Piper/Matcha token maps generated and diffed.

================================================================================
2. PHASE 1 — FRONTEND CORE (the engine-agnostic brain)
================================================================================
GOAL: Devanagari(+Latin) text → canonical phone sequence, deterministically,
with per-word trace, using the Standard's rules.

Steps:
  1.1 normalize.py — NFC (R1.3), virama detect (R1.4), akshara tokenize.
  1.2 inventory.py — segmental maps (R2.1–R2.4): C→phone, matra→vowel,
      व→/b|w/, visarga→silent.
  1.3 rules.py — medial /a/ (R3.1/R3.2/R3.3/R3.5/R3.5b), final-schwa U5
      (import u5 from Standard; C0–C6 + L_neg), sandhi (R7), length (R9.2).
  1.4 normalize_text.py — number verbalization (Nepali word order), punctuation
      → pause tokens, abbreviation expansion, Latin code-switch (IndicXlit
      transliterate OR letter-by-letter, configurable; default transliterate).
  1.5 lexicon.py — load data/lexicon_seed.tsv (7282, spec-traceable). Lookup
      first; on MISS, run U5 rules (NEVER blind letter fallback — fixes Ampixa's
      #1 error). Log every OOV + its rule-derived pronunciation.
  1.6 trace.py — emit SPEC §12 trace for every word.
  Acceptance: `nspc --text "विकास घर हुन्"` → correct canonical sequence with
  trace; OOV sentence produces rule-derived phones, zero silent drops.

================================================================================
3. PHASE 2 — UNIVERSAL ADAPTERS + CLI (the "kit" interface)
================================================================================
GOAL: translate canonical → whatever a consumer needs. Each adapter is pure
function(canonical) → target; no linguistic logic inside.

  2.1 ipa.py — canonical → IPA (for humans / publication).
  2.2 json.py — canonical → {text, phones, trace, oov[]} (for pipelines).
  2.3 piper.py — canonical → Piper `phoneme_id_map` (text mode) or pre-built
      `phoneme_ids`. Includes a script to write config.json snippets.
  2.4 matcha.py — canonical → Matcha `tokens.txt` + a `nepali_cleaners` stub
      showing where to plug the call (mirrors mah92 Persian recipe).
  2.5 cli.py — `nspc --text "..." --format ipa|json|piper|matcha`.
  Acceptance: each adapter output parses by the target trainer's loader; round-
  trip (canonical→adapter→trainer-token→id) is stable.

================================================================================
4. PHASE 3 — VALIDATION HARNESS (prove it before pushing)
================================================================================
  3.1 test_unit.py — SPEC §12 worked examples (विकास, घर, हुन्, छन्, हुन्छ,
      मञ्च, यस, पार्क) assert branch + action + IPA.
  3.2 test_regression.py — full 7282 + 117 held-out via lexicon/rule path;
      exit non-zero on any divergence from the Standard's ground truth.
  3.3 test_adapters.py — every adapter emits a valid token sequence; inventory
      coverage 100% (no phone outside INVENTORY.md).
  3.4 data/sample_sentences.txt — real held-out sentences; assert no OOV silent
      drop, gemination/tatsama/foreign branches fire.
   Acceptance: `pytest` green; coverage of inventory = 100%; regression = 100%.
   3.5 differential_demo.py — AUTO-GENERATES docs/benchmark_differential.md by
       rendering the tricky-word set through nspc AND (if espeak-ng present)
       eSpeak `ne`, tabulating per-word differences with the U5 branch cited.
       Implements TEST_STRATEGY.md T3; the v0.1 table is hand-populated from
       established eSpeak/Ampixa behavior and is replaced by this script.
   3.6 test_native_audit.py — ~200-row curated CSV (word|expected_IPA|U5_branch);
       asserts our output matches expected. TEST_STRATEGY.md T4.
   3.7 test_oov.py — 500 lexicon-absent words; assert rule-derived pronunciation,
       zero silent drops, all tokens ∈ INVENTORY.md. TEST_STRATEGY.md T5.
   See docs/TEST_STRATEGY.md for the full runnable-now vs needs-model split.

================================================================================
5. PHASE 4 — PACKAGING & DOCS (GitHub push-ready)
================================================================================
  4.1 pyproject.toml — `pip install nspc`, entry point `nspc`.
  4.2 README.md — install, 30-sec example, link to Standard v1.0.
  4.3 docs/INVENTORY.md, TTS_INTEGRATION_PLAN.md, IMPLEMENTATION_ROADMAP.md.
  4.4 examples/piper_dataset + examples/matcha_dataset — copy-paste training
      prep showing OUR frontend replacing eSpeak/Ampixa.
  4.5 CITATION.cff — Standard v1.0 + primary sources + prior art (Ampixa, eSpeak).
  Acceptance: `pip install -e .` works; `nspc --text "नमस्ते"` prints phones;
  examples run end-to-end up to the trainer's preprocess step.

================================================================================
6. MILESTONES (suggested commit cadence for GitHub)
================================================================================
  M0  repo scaffold + INVENTORY.md + inventory.py          (Phase 0)
  M1  normalize + rules + u5 (port from Standard)          (Phase 1.1–1.3)
  M2  normalize_text + lexicon + trace                    (Phase 1.4–1.6)
  M3  adapters ipa/json + cli                             (Phase 2.1–2.5)
  M4  piper + matcha adapters                             (Phase 2.3–2.4)
  M5  full test suite green                               (Phase 3)
  M6  packaging + examples + docs + CITATION              (Phase 4)
  M7  push to GitHub, tag v0.1.0

================================================================================
7. SCOPE BOUNDARY (explicit, per your direction)
================================================================================
  IN: universal frontend, inventory, adapters, docs, tests, GitHub push.
  OUT: training the acoustic model, vocoder, recorded dataset collection.
       Those are downstream consumers of this kit, not part of it.
  REJECTED AS PHONEMIZER: eSpeak `ne` (wrong affricates/gemination/schwa).
  REFERENCE ONLY: Ampixa real_nepali (prior art; 48k lexicon as cross-check
       source, re-audited against U5 before any inclusion).
