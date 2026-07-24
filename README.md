# NSPC Kit — Nepali Speech Phones Kit

**Universal, engine-agnostic G2P frontend for Standard Nepali**

Converts Devanagari (with Latin code-switch) text to canonical phoneme sequences that any TTS trainer can consume — Piper, Matcha-TTS, VITS, Coqui, ONNX, or plain IPA. No trained voice; the kit is the deterministic frontend, canonical phone inventory, and adapter layer that make correct Nepali TTS training possible.

## Why this exists

There is no proper open-source G2P mapping for Nepali. Existing solutions have known errors:

- **Wrong affricates** (alveolar instead of palatal च/छ)
- **Dropped gemination** (no surface distinction between क and क्क)
- **Heuristic schwa deletion** (~5% error rate)
- **Letter-fallback** for unknown words

NSPC Kit replaces these with:

- A **deterministic, rule-based system** — U5 final-schwa decision tree (C0 → C6 priority) with L_neg + length + dead-consonant constraints
- **Native-speaker validated** pronunciation against the Nepal Academy corpus
- A **canonical phone inventory** every adapter translates from, never invents
- A lexicon fallback that uses **rules, not letters**, for unknown words

> *eSpeak `ne` is not used* — its affricates are wrong, gemination is dropped, and its schwa deletion is unprincipled.

## Quick Start

```bash
pip install -e .

# Basic usage — IPA output
nspc --text "विकास घरमा छन्" --format ipa
# विकास घरमा छन् -> b ʋ i k aː s ɡʱ ə r m aː tʃʰ ə n

# Single-word JSON with trace
nspc --text "नमस्ते" --format json
# {"text": "नमस्ते", "phones": "N a m a s T e", ...}

# TTS-trainable outputs
nspc --text "नमस्ते" --format piper    # Piper phoneme_id_map ready
nspc --text "नमस्ते" --format matcha   # Matcha tokens.txt ready
```

## Features

| Feature                 | Example        | Output                                       |
| ----------------------- | -------------- | -------------------------------------------- |
| Cardinal numbers        | 2026           | दुई हजार छब्बिस                              |
| Decimals                | 12.5           | बाह्र पोइन्ट पाँच                              |
| Mobile numbers          | 9849658494     | नौ आठ चार नौ छ पाँच आठ चार नौ चार              |
| Fractions               | १/२            | एक बाइ दुई                                   |
| Percentages             | 50%            | पचास प्रतिशत                                   |
| Mixed-script (Latin in) | `facebook`     | फेसबुक                                       |

**Linguistic rules implemented:**

- Native schwa deletion — U5 priority tree (C0 → C6) with L_neg and length gating
- Conjuncts: क्ष, ज्ञ, त्र, श्र, स्त, स्म, द्र, क्र, ग्र, प्र + ञ-before-palatal family (ञ्च, ञ्छ, ञ्ज)
- Nasal marks: ँ (chandrabindu = vowel nasalisation) and ं (anusvara = place-assimilated nasal consonant)
- Aspirated-final retains inherent /a/ (दुख → `dukha`, सुख → `sukha`)
- Postposition joins (नेपालको → `nepalko`)
- Liquid/glide medial coda (सरकार → `sarkaːr`)
- Verb-final live endings (भन्छ → `bhantʃʰ`)

## Installation

```bash
# Core only — pure Python, no ML dependencies
pip install -e .

# Optional: ML-based transliteration for unknown Latin tokens
pip install indicxlit
```

## Usage

### Command line

```bash
# Convert a Devanagari phrase to IPA
nspc --text "अनलाइन विकास" --format ipa

# Process all lines of an input file
nspc --file sentences.txt --format json

# Print canonical inventory files for TTS trainers
nspc --tokens-file        # canonical phone tokens
nspc --piper-map          # Piper phoneme_id_map.ready
nspc --matcha-tokens      # Matcha tokens.txt
```

### Python API

```python
from nspc.core import lexicon as L
from nspc.core.adapters import ipa
from nspc.core.normalize_text import normalize_text_pipeline

# Convert a single word
tokens, tags, branch, retain, source = L.process("विकास")
# tokens: ['b', 'i', 'k', 'a:', 's']
# branch: C6, retain: False

print(ipa.convert(tokens))
# Output: b i k aː s

# Handle Romanised / numeric code-switch in running text
text = normalize_text_pipeline("kathmandu 2026 साल")
# Output: काठमाडौं दुई हजार छब्बिस साल
```

## Project Structure

```
nspc/
├── cli.py                 # command-line entry point
├── core/
│   ├── inventory.py       # canonical phone inventory (21 V + 23 C)
│   ├── normalize.py       # NFC + NFC tagging
│   ├── u5_reference.py    # final-schwa decision (C0–C6)
│   ├── rules.py           # segmental realisation, conjunct map, nasal rules
│   ├── lexicon.py         # seed lexicon + curated overrides
│   ├── numbers.py         # cardinal / decimal / mobile / fraction / percent
│   ├── mixed_script.py    # Roman → Devanagari preprocessing
│   └── adapters/          # IPA, JSON, Piper, Matcha, Kokoro
└── cli.py

docs/
├── SPECIFICATION.md       # authoritative linguistic rules
├── INVENTORY.md           # canonical phone inventory (with examples)
└── METHODOLOGY.md         # validation methodology

tests/                     # unit + standard + native-ear + numbers + adapters (8 suites)
data/                      # seed corpus (Excel) + regression TSV
examples/                  # Piper / Matcha / Kokoro copy-paste snippets
```

## Validation Status

- 7,282-row Academy seed corpus: 100% agreement
- 117-word external held-out: 100% agreement
- 8 unit / regression / native-ear test suites (all pass)
- Engine output strictly constrained to the 21-vowel / 23-consonant canonical inventory
- Only a small number of true lexical exceptions remain in the curated lexicon — see `docs/AUDIT_LEXICON_OVERRIDES.md`

## Citation

See `CITATION.cff` for the citation format (CFF 1.2.0; cites the Standard v1.0, the primary scholarly sources, and prior G2P attempts).

## License

MIT. See `LICENSE`.
