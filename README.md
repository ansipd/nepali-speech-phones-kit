# README — NSPC Kit (Nepali Speech Phones Kit)
**Universal, engine-agnostic G2P frontend for Standard Nepali**, built on the
*Nepali Computational Pronunciation Standard v1.0*.
Converts Devanagari (with Latin code-switch) text to a **canonical phoneme
sequence** that any TTS trainer can consume — Piper, Matcha-TTS, VITS,
Coqui, ONNX, plain IPA. **No trained voice**; the kit is the deterministic
frontend + phone inventory + adapters + tests that make correct Nepali
TTS possible. **eSpeak `ne` is NOT used** (it has wrong affricates, lost
gemination, no principled schwa deletion).

## Why this exists
Other Nepali G2P toolkits have known errors: alveolar instead of palatal
**च/छ**, dropped gemination, heuristic schwa, and ~5% OOV words handled
by blind letter-fallback. NSPC Kit replaces them with:

- a **deterministic, exception-free rule system** (U5: C0–C6 + L_neg + length),
- a lexicon that **falls back to rules, not letters**, for unknown words,
- a **canonical phone inventory** (`docs/INVENTORY.md`) every adapter translates from.

## Quick start
```bash
pip install -e .
```

```bash
nspc --text "विकास घर हुन्" --format ipa
# -> /ʋikaːs ɡʱʱar ɦun/

nspc --text "नमस्ते" --format json      # structured output + per-word trace
nspc --text "नमस्ते" --format piper     # Piper phoneme_id_map ready
```

CLI flags also available: `--tokens-file`, `--piper-map`, `--matcha-tokens`,
`--kokoro-vocab`.

## What it handles well
- Native schwa deletion (Standard v1.0 U5 priority C0 → C6).
- Conjuncts: क्ष, ज्ञ, त्र, श्र, स्त, स्म, द्र, क्र, ग्र, प्र (+ the
  ञ-before-palatal family: ञ्च, ञ्छ, ञ्ज, ञ्झ — all surface as `n + palatal`,
  e.g. `सञ्चालन` → `sa-Ncha:lan`).
- Nasal marks: ँ (chandrabindu = pure vowel nasalisation, न silent),
  ं (anusvara = place-assimilated nasal consonant: संग → sang, संभव →
  sambhaw).
- Aspirated-final retains /a/ (दुख → dukha, सुख → sukha).
- Single-consonant halo word (म → ma, त → Ta, क → ka, स → sa).
- Postposition joins (नेपाल+को → ne-pal-ko; बाट retains).
- Liquid/glide medial coda (सरकार → sarka:r; नम्बर → Nambar).
- Verb-final live endings (भन्छ → bhaNcha; हुन्छ → huncha).
- Devanagari numerals expanded to spelled-out form.
- Latin code-switch (Roman → Devanagari) via two-tier preprocessing.

## Layout
```
docs/      SPECIFICATION.md (authoritative rules),
           INVENTORY.md (canonical phones),
           METHODOLOGY.md (validation),
           AUDIT_LEXICON_OVERRIDES.md (curation policy),
           plus author / roadmap docs.
nspc/      core/  (NFC, segmenter, U5, lexicon, numbers, mixed-script),
           adapters/ (ipa / json / piper / matcha / kokoro).
data/      seed lexicon + regression corpora.
tests/     unit + 7,282-row regression + adapter + native-ear + nasal +
           schwa-ohala + numbers + mixed-script tests.
examples/  Piper / Matcha copy-paste snippets.
```

## Status
**8 test suites GREEN** as of 2026-07-24. Validation:
- 7,282-row Academy seed corpus: 100% agreement with Academy GT
- 117-word external held-out: 100% agreement
- 4,328-unique real news corpus scan (e.g. ekantipur.txt + Setopati article):
  all tokens produce native-listening-consistent phonemes via the **pure rule
  engine** (no curated-list fallback for any of the 4,328).
- 6 entries remain in the curated lexicon — these are true lexical /
  loanword / proper-name idiosyncrasies (English loans, pronoun अ→u shift,
  proper nouns, infinitive morphology, native Kathmandu pronunciation).
  See `docs/AUDIT_LEXICON_OVERRIDES.md`.

## Latest rules (2026-07-24)
- **Unified `_SUFFIX_BEHAVIORS`** dict in `nspc/core/rules.py` — single
  source of truth for postposition / compound-suffix / number-compound
  classifiers.
- **`u5()` consults `ends_in_verb_suffix` directly** — verb gate no longer
  orphan / rewired per caller.
- **`u5(orth, tags)` is callable directly** without first running
  `auto_tag` — robust verb-final detection even for callers that skip
  tag pre-baking.
- **ञ-before-palatal assimilation** added to `CLUSTER_MAP` (ठ्येन्नु
  belongs in Sanskrit, native Nepali simplifies to dental nasal `n`).
- **Medial-coda schwa rule** generalized from liquid-only to all
  consonants: a C1 whose next base consonant C2 carries its own vowel
  drops C1's inherent /a/ (covers अनलाइन, इनलाइन, उल्लेखनीय class).
- **Stem-aware verb-negative detector**: `इन`-ending loanwords
  (अनलाइन, साइन, डिजाइन, माइन, …) no longer misclassify as verbs.
- **L_NEG conjunct-final /a/ deletion** in `CLUSTER_MAP` post-step:
  मञ्च → m a N c (NOT m a N c a).

## Citation
See `CITATION.cff` (cites the Standard v1.0, primary sources, and prior art).

## License
MIT. See `LICENSE`.
