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

### KEEP — genuinely irregular (8 entries remain curated)
Each is assessed for whether a general RULE could subsume it. The ones marked
"rule-able (needs native confirmation on more words)" are phonotactic patterns
but are NOT yet generalized because we lack corpus evidence and a broad rule
could wrongly change other words. They stay curated until native-reviewed.

| Word | Tokens | Why curated | Rule-able? |
|------|--------|-------------|------------|
| पार्क | pa:rk | foreign loan C5 | TABBED: foreign detection (future) |
| विकास | wika:sa | tatsama C4 retain | Already a rule (tatsama→RETAIN); curated only to supply the `tatsama` tag (auto_tag can't guess etymology). |
| यस | yus | अ→u sound change | Genuine irregular — no rule. |
| उसले | usle | pronoun उस + ले join (host final schwa deleted) | NOW RULE-BASED: R7 join fix (host_drops_final_a = not host_retain). Covers उसले/जसले/कसले/उनले/त्यसले/कुनले. Override deleted. |
| सरकार | sarkar | medial schwa after स deleted | Pattern (schwa after स) — rule-able with native confirmation. |
| मञ्च | manch | ञ→n assimilation (speech variant) | Spelling-equivalent with मंच (anusvara); both map to मञ्च via normalize._SPELLING_VARIANTS. |
| अनलाइन | aNliN | medial schwas deleted | Loan "online"; falls under schwa-after-स pattern. |
| हिँड्न | hidnu | infinitive न् retained | Genuine irregular (infinitive morphology). |
| काठमान्डु | kathamandu | proper noun, native spelling | Genuine irregular (place name). |

> `दुख`/`सुख` overrides DELETED (2026-07-19): now covered by new U5 **C5b**
> aspirated-final rule — any native word ending in an aspirated stop/affricate
> (ख/घ/छ/झ/ठ/ढ/थ/ध/फ/भ) keeps its final inherent /a/. Phonotactic class rule,
> not a word list. दुख->Dukha, सुख->sukha.

> `म` override DELETED (2026-07-19): single live consonant now RETAINED via
> new U5 C-HALO branch + `is_halo` in normalize.auto_tag. म→ma, त→Ta, क→ka,
> स→sa, etc. all rule-derived.

## REMAINING RULE-BASED OPPORTUNITIES (future sessions, native confirmation needed)
1. **सरकार/अनलाइन** → medial schwa deletion (compound/join). सरकार: सर+कार,
   र's final अ drops (word-specific, no safe general rule). अनलाइन: loan.
2. **पार्क** → foreign-loan detection (tabled).
3. **विकास** → supply tatsama tag via a classifier (currently curated only for its
   etymology tag; the retain behaviour is already a rule).

## NATIVE REVIEW NOTES (2026-07-19, joint review of the 9)
- **यस**: yus / yas / yes all sound identical to native ear -> curated `yus`
  kept, no change.
- **मञ्च / मंच**: confirmed the SAME word (two spellings, anusvara vs conjunct).
  normalize._SPELLING_VARIANTS maps मंच -> मञ्च, so both yield "manch".
- **उसले**: productive pronoun+ले pattern (उस/यस/जस/कस/उन/त्यस/कुन + ले). Now
  RULE-BASED via R7 join fix: host_drops_final_a = (not host_retain). Covers
  उसले->usle, जसले->jasle, कसले->kasle, उनले->uNle, etc. Override DELETED.
- **सरकार**: सर+कार compound where र's final अ drops. Word-specific (no safe
  general rule without a stem-splitter); remains curated.
- **विकास, अनलाइन, हिँड्न, काठमान्डु, पार्क**: confirmed keep as curated.

## FINAL STATE (2026-07-19)
- 15 redundant overrides deleted; rule engine is authoritative over unreliable
  seed GT (L.process routes seed-only words to pure rule).
- 2 rule generalizations added: C-HALO (single consonant keeps अ) and C5b
  (aspirated-final keeps अ) — together removed म, दुख, सुख.
- Lexicon now holds **8 genuine irregularities** (table above). Every other
  word in the 942-unique corpus resolves via the deterministic rule engine.
- 5 test suites GREEN, including the ँ/ं nasal split regression (R3.4).

