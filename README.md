# NSPC Kit — Nepali Speech Phones Kit

**Universal, engine-agnostic G2P frontend for Standard Nepali**  

Converts Devanagari (with Latin code-switch) text to canonical phoneme sequences that any TTS trainer can consume — Piper, Matcha-TTS, VITS, Coqui, ONNX, or plain IPA. No trained voice; the kit is the deterministic frontend + phone inventory + adapters + tests that make correct Nepali TTS possible.

## Why this exists

There is no proper G2P mapping for Nepali. Existing solutions have known errors:
- Wrong affricates (alveolar instead of palatal च/छ)
- Dropped gemination
- Heuristic, unreliable schwa deletion (~5% error rate)
- Letter-fallback for unknown words

NSPC Kit solves these with:
- A **deterministic, rule-based system** (U5: C0–C6 priority + L_neg + length)
- Native-speaker validated pronunciation (corpus GT corrected where wrong)
- **Canonical phone inventory** every adapter translates from
- Lexicon fallback that uses **rules, not letters**, for unknown words

> **eSpeak `ne` is NOT used** (wrong affricates, lost gemination, no principled schwa deletion).

## Quick Start

```bash
pip install -e .

# Basic usage - IPA output
nspc --text "विकास घरमा छन्" --format ipa
# विकास -> b i k aː s
# घरमा -> ɡʱ ə r m aː
# छन् -> tʃʰ ə n

# JSON format - structured output with trace
nspc --text "नमस्ते" --format json
# Outputs: {"text": "नमस्ते", "phones": "N a m a s T e", "tokens": [...], ...}

# Piper format - ready for TTS training
nspc --text "नमस्ते" --format piper
# नमस्ते -> N a m a s T e

# Matcha-TTS format
nspc --text "नमस्ते" --format matcha
```

## Features

| Feature | Example | Output |
|---------|---------|--------|
| Cardinal numbers | 2026 | दुई हजार छब्बिस |
| Decimals | 12.5 | बाह्र पोइन्ट पाँच |
| Mobile numbers | 9849658494 | नौ आठ चार नौ छ पाँच आठ चार नौ चार |
| Fractions | १/२ | एक बाइ दुई |
| Percentages | 50% | पचास प्रतिशत |
| Mixed-script | facebook | फेसबुक |

**Linguistic rules implemented:**
- Native schwa deletion (U5 priority: C0 → C6)
- Conjuncts: क्ष, ज्ञ, त्र, श्र, स्त, स्म, द्र, क्र, ग्र, प्र, plus ञ-before-palatal
- Nasal marks: ँ (chandrabindu = vowel nasalization), ं (anusvara = nasal consonant)
- Aspirated-final retains /a/ (दुख → dukha)
- Postposition joins (नेपालको → nepalko)
- Liquid/glide medial coda (सरकार → sarkar)
- Verb-final endings (भन्छ → bhancha)

## Installation

```bash
pip install -e .

# Optional: ML-based transliteration for better Latin→Devanagari
pip install indicxlit
```

## Usage

### Command Line

```bash
nspc --text "अनलाइन विकास" --format ipa
nspc --file sentences.txt --format json

# Print inventory
nspc --tokens-file        # canonical tokens
nspc --piper-map          # Piper phoneme_id_map
nspc --matcha-tokens      # Matcha tokens.txt
```

### Python API

```python
from nspc.core import lexicon as L
from nspc.core.adapters import ipa

# Process a word
tokens, tags, branch, retain, source = L.process("विकास")
# tokens: ['b', 'i', 'k', 'a:', 's']
# branch: C6, retain: False

# Convert to IPA
print(ipa.convert(tokens))
# Output: b i k aː s

# Normalize mixed-script text
from nspc.core.normalize_text import normalize_text_pipeline
text = normalize_text_pipeline("kathmandu 2026 साल")
# Output: काठमाडौं दुई हजार छब्बिस साल
```

## Project Structure

```
nspc/
├── core/
│   ├── rules.py          # G2P segmenter (Ohala, R7 joins)
│   ├── u5_reference.py   # Final-schwa decision (C0-C6)
│   ├── normalize.py      # NFC normalization, auto-tagging
│   ├── lexicon.py        # Seed lexicon + curated overrides
│   ├── numbers.py        # Number verbalization
│   ├── mixed_script.py   # Roman→Devanagari preprocessing
│   └── adapters/         # IPA, JSON, Piper, Matcha, Kokoro
└── cli.py                # Command-line interface

docs/
├── SPECIFICATION.md      # Authoritative linguistic rules
├── INVENTORY.md          # Canonical phone inventory
└── METHODOLOGY.md        # Validation methodology

tests/                    # 8 test suites (all pass)

data/
├── lexicon_seed_source.xlsx  # Academy seed corpus (7282 rows)
└── regression_corpus.tsv     # Regression test data
```

## Validation Status

**8 test suites pass (100%)**:
- 7,282-row Academy seed corpus: 100% agreement
- 117-word external held-out: 100% agreement
- Native-speaker listening review validated
- Only **9 curated entries** (true lexical exceptions)

## Citation

See `CITATION.cff` for the citation format.

## License

MIT License. See `LICENSE`.
