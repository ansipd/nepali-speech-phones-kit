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
| उसले | usle | monosyllabic host उस + ले (host final schwa deleted) | Curated: the R7 join `host_drops_final_a` path only fires for polysyllabic hosts (`_host_cons > 1 or virama`), so monosyllabic pronoun hosts (उस/कस/जस/उन/त्यस/कुन) are NOT auto-covered. Curated list supplies उसले; the remaining joins (जसले/कसले/उनले/त्यसले/कुनले) resolve via the same path once added, or via rule (e.g. कस→kas drops, जस→jas drops). |
| सरकार | sarkar | medial schwa after र deleted (liquid coda) | NOW RULE-BASED: Ohala internal-schwa rule (liquids/glides as medial codas) in rules.py `_ohala_internal_schwa`. Covers सरकार/तरबार/सलवार/तलवार. Override DELETED; rule produces `sarka:r`. |
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
1. **अनलाइन** → medial schwa deletion (loan "online"). Falls under the Ohala
   liquid-coda pattern in spirit but its structure (न-ल-इ-न) is not a liquid
   coda; still curated pending a broader medial-schwa rule.
2. **पार्क** → foreign-loan detection (tabled).
3. **विकास** → supply tatsama tag via a classifier (currently curated only for its
   etymology tag; the retain behaviour is already a rule).

## NATIVE REVIEW NOTES (2026-07-19, joint review of the 9)
- **यस**: yus / yas / yes all sound identical to native ear -> curated `yus`
  kept, no change.
- **मञ्च / मंच**: confirmed the SAME word (two spellings, anusvara vs conjunct).
  normalize._SPELLING_VARIANTS maps मंच -> मञ्च, so both yield "manch".
- **उसले**: productive pronoun+ले pattern (उस/यस/जस/कस/उन/त्यस/कुन + ले). The R7
  join `host_drops_final_a` path fires only for polysyllabic hosts
  (`_host_cons > 1 or virama`); monosyllabic pronoun hosts are NOT auto-covered,
  so उसले is kept CURATED (usle). Other monosyllabic joins (जसले/कसले/उनले/...)
  either resolve via the rule's own final-schwa deletion (e.g. कस->kas, जस->jas
  drop standalone) or can be added to the curated list if listening shows a
  mismatch.
- **सरकार**: NOW RULE-BASED via the Ohala internal-schwa rule (liquids as medial
  codas). सरकार = स(keeps) र(coda, drops) कार -> sarka:r. The same rule yields
  तरबार->Tarba:r, सलवार->salwa:r, तलवार->Talwa:r. Curated override DELETED.
- **विकास, अनलाइन, हिँड्न, काठमान्डु, पार्क**: confirmed keep as curated.

## FINAL STATE (2026-07-19, updated 5g)
- 15 redundant overrides deleted; rule engine is authoritative over unreliable
  seed GT (L.process routes seed-only words to pure rule).
- 3 rule generalizations added: C-HALO (single consonant keeps अ), C5b
  (aspirated-final keeps अ), and the Ohala liquid-coda rule (liquids/glides drop
  their inherent /a/ as medial codas) — together removed म, दुख, सुख, सरकार.
- Lexicon now holds **8 genuine irregularities** (table above: पार्क, विकास, यस,
  उसले, मञ्च, अनलाइन, हिँड्न, काठमान्डु). Every other word in the 942-unique
  corpus resolves via the deterministic rule engine.
- 6 test suites GREEN (unit + 7282-row regression + no-trailing-schwa +
  matra-inventory + nasal ँ/ं split + Ohala liquid-coda regression).

