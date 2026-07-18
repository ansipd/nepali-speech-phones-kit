# Nepali Speech→Phones Conversion Kit (NSPC-Kit)

A **universal, engine-agnostic** grapheme-to-phoneme (G2P) frontend for
Standard Nepali, built on the *Nepali Computational Pronunciation Standard
v1.0* (a deterministic linguistic specification validated 100% on a 7282-word
Academy-consistent corpus and 117 genuinely held-out external words).

It converts Nepali Devanagari (with Latin code-switching) text into a
**canonical phoneme sequence** that any TTS trainer can consume via a thin
adapter — Piper, Matcha-TTS, VITS, Coqui, ONNX, or plain IPA.

> This is **not** a trained voice. It is the frontend + phone inventory +
> adapters + docs + tests that make training a *correct* Nepali TTS possible.
> eSpeak `ne` is explicitly **not** used as the phonemizer (wrong affricates,
> lost gemination, no principled schwa deletion).

## Why this exists
Existing Nepali G2P (eSpeak `ne`; Ampixa `real_nepali`) has known errors:
alveolar instead of palatal च/छ, dropped gemination, heuristic schwa, and
~5% OOV words handled by blind letter-fallback. NSPC-Kit replaces them with a
deterministic, exception-free rule system (U5: C0–C6 + L_neg + length) plus a
lexicon that falls back to **rules, not letters**, for unknown words.

## Install
```bash
pip install -e .
```
Requires Python 3.10+.

## 30-second example
```bash
nspc --text "विकास घर हुन्" --format ipa
# -> /ʋikaːs ɡʱʱar ɦun/
nspc --text "नमस्ते" --format json      # structured output + per-word trace
nspc --text "नमस्ते" --format piper     # Piper phoneme_id_map ready
```

## Layout
```
docs/      SPECIFICATION.md (the authoritative linguistic rules),
           DEPENDENCIES.md, METHODOLOGY.md, TTS_INTEGRATION_PLAN.md,
           IMPLEMENTATION_ROADMAP.md, INVENTORY.md
nspc/      core/ (engine-agnostic frontend) + adapters/ (format translators)
data/      seed lexicon + regression corpora
tests/     unit + regression + adapter tests (pytest)
examples/  copy-paste Piper / Matcha dataset prep
```

## Status
Planned → implementation in progress (see `docs/IMPLEMENTATION_ROADMAP.md`).
Phase 0 (phone inventory) is the next commit.

## License
MIT. See `LICENSE`.

## Citation
See `CITATION.cff` (cites the Standard v1.0, primary sources, and prior art).
