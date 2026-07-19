# AUDIT — Lexicon Curated Overrides vs Pure Rule
**Date**: 2026-07-19
**Scope**: curated entries in `nspc/core/lexicon.py::_load_curated`
**Method**: compare lexicon output vs pure-rule output (`rules.segment`).

> NOTES:
> - `घर` and `कमल` moved to HALANTA_FINAL (commit af67f17).
> - Matra-length words (पुस्तकालय, अर्थशास्त्र, मित्रता, साहित्य, सफलता,
>   प्रधानमन्त्री, चिनियाँ): native review confirmed every ा = LONG (a:).
>   The lexicon short-form overrides were DEVIATIONS. All deleted; rule wins.
> - **Seed GT is unreliable** (project methodology). `L.process` now routes
>   seed-only entries to the PURE RULE (ignoring corpus GT branch/retain).
>   Only CURATED entries override the rule. This fixed 3 latent seed errors
>   (भन्छ/सुत्छ → C2b retain; स्कन्ध → C1 conjunct retain) that the curated
>   overrides had been masking.

## RESULT (after cleanup, commit 2026-07-19)

### Deleted as redundant (rule already correct) — 15 entries
देश, भन्छ, सुत्छ, हुन्छ, भएन, देशतिर, स्कन्ध, स्कुल, पुस्तकालय,
अर्थशास्त्र, मित्रता, साहित्य, सफलता, प्रधानमन्त्री, चिनियाँ.

All now resolve via the rule engine (src=rule). Zero behaviour regression
(verified: भन्छ→bhaNcha, स्कन्ध→skaNDha, पुस्तकालय→pusTaka:laya, etc.).

### KEEP — genuinely irregular (9 entries remain curated)
| Word | Tokens | Why curated |
|------|--------|-------------|
| पार्क | pa:rk | foreign loan C5 (foreign detection TABBED) |
| विकास | wika:sa | tatsama C4 retain (kept for clarity) |
| यस | yus | अ→u sound change (irregular) |
| उसले | usle | medial schwa after स deleted |
| सरकार | sarkar | medial schwa after स deleted |
| मञ्च | manch | ञ→n assimilation |
| अनलाइन | aNliN | medial schwas deleted |
| हिँड्न | hidnu | infinitive न् retained |
| काठमान्डु | kathamandu | proper noun, native spelling |

> `दुख`/`सुख` overrides DELETED (2026-07-19): now covered by new U5 **C5b**
> aspirated-final rule — any native word ending in an aspirated stop/affricate
> (ख/घ/छ/झ/ठ/ढ/थ/ध/फ/भ) keeps its final inherent /a/. Phonotactic class rule,
> not a word list. दुख->Dukha, सुख->sukha.

> `म` override DELETED (2026-07-19): single live consonant now RETAINED via
> new U5 C-HALO branch + `is_halo` in normalize.auto_tag. म→ma, त→Ta, क→ka,
> स→sa, etc. all rule-derived.

## REMAINING RULE-BASED OPPORTUNITIES (future sessions)
1. **मञ्च** → ञ→n assimilation rule.
2. **उसले/सरकार/अनलाइन** → medial schwa-deletion-after-स/र pattern (R7-general).
3. **पार्क** → foreign-loan detection (tabled).

