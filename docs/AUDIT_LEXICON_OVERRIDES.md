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

### KEEP — genuinely irregular (11 entries remain curated)
| Word | Tokens | Why curated |
|------|--------|-------------|
| पार्क | pa:rk | foreign loan C5 (foreign detection TABBED) |
| विकास | wika:sa | tatsama C4 retain (kept for clarity) |
| दुख | dukha | final अ kept (RETAIN_FINAL candidate) |
| सुख | sukha | final अ kept (RETAIN_FINAL candidate) |
| यस | yus | अ→u sound change (irregular) |
| उसले | usle | medial schwa after स deleted |
| सरकार | sarkar | medial schwa after स deleted |
| मञ्च | manch | ञ→n assimilation |
| अनलाइन | aNliN | medial schwas deleted |
| हिँड्न | hidnu | infinitive न् retained |
| काठमान्डु | kathamandu | proper noun, native spelling |

> `म` override DELETED (2026-07-19): single live consonant now RETAINED via
> new U5 C-HALO branch + `is_halo` in normalize.auto_tag. म→ma, त→Ta, क→ka,
> स→sa, etc. all rule-derived.

## REMAINING RULE-BASED OPPORTUNITIES (future sessions)
1. **दुख/सुख** → RETAIN_FINAL class.
2. **मञ्च** → ञ→n assimilation rule.
3. **उसले/सरकार/अनलाइन** → medial schwa-deletion-after-स/र pattern (R7-general).
4. **पार्क** → foreign-loan detection (tabled).

