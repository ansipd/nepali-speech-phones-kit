# PROGRESS LOG — Nepali Speech Phones Kit (NSPC-Kit)

**Project**: Deterministic, citable Nepali pronunciation Standard v1.0 + universal
engine-agnostic G2P frontend for TTS training (no trained voice).
**Location**: `C:\Users\Sandip Ghimire\nepali-speech-phones-kit\`
**Status**: All 5 test suites GREEN as of 2026-07-19. Lexicon pruned to 8
genuine irregularities; rule engine now authoritative over unreliable seed GT;
nasal ँ/ं split regression-locked (R3.4).

---

## 0. METHODOLOGY (the rules we work by)

- Native-speaker ear is the authority. Corpus GT (nepali_g2p_corpus.xlsx) was
  found UNRELIABLE for final-schwa and conjunct realization — kit corrects it.
- Every statement needs evidence; no "probably / it seems / many speakers".
- Minimize exceptions; generalize every rule; when a rule can't be generalized,
  curate the specific word in the lexicon (authoritative tokens).
- Spec (docs/SPECIFICATION.md) is authoritative; reference impl is replaceable.
- User is NOT a coder — communicate via plain-letter readings, not IPA/code.
- Terminal/PowerShell mangles Devanagari — write UTF-8 files for Notepad review.

## 1. ARCHITECTURE (built, stable)

```
nspc/core/
  normalize.py     NFC + auto_tag (derives U5 tag tuple from orthography)
  inventory.py     canonical phone inventory (vowels + consonants)
  u5_reference.py  U5 unified priority rule (C0..C6) + independent ground_truth
  rules.py         segment() : Devanagari -> canonical tokens; CLUSTER_MAP; R7
  lexicon.py       seed (942 unique words) + curated overrides + OOV fallback
  adapters/        ipa / json / piper / matcha  (engine-agnostic consumers)
  cli.py           `nspc --text ... --format ...`
tests/
  test_standard_regression.py   unit traces + 7282-row corpus regression (GREEN)
  test_no_trailing_schwa.py     Kala 'r ax' defect guard (GREEN)
   test_native_audit.py          29 curated native-validated tokens (GREEN)
   test_nasal_anusvara_chandrabindu.py  ँ vs ं split regression (R3.4, GREEN)
docs/
  SPECIFICATION.md   authoritative standard v1.0 (+ T6 addendum appended)
  INVENTORY.md        canonical phone inventory
nspc/tools/review.py  T6 review (--out writes UTF-8 file)
data/sample_sentences.txt  10 T6 sentences
```

## 2. CORE LINGUISTIC RULES (validated)

### Inherent vowel
- Inherent vowel = /a/, realized [ə]~[ʌ]; canonical token `a`.
- Inventory: T Th D Dh N = DENTAL (t th d dh n); t th d dh n = RETROFLEX
  (ʈ ʈʰ ɖ ɖʱ ɳ). Verified: सुत्छ = s-u-T-ch-a (dental T).

### U5 priority (first match wins) — FINAL schwa
- C0: ends in virama (dead) -> DELETE (हुन्, छन्, हुन्छन्)
- C1: conjunct-final -> RETAIN; C1-Lneg (मञ्च/गञ्ज/पन्त) -> DELETE
- C2: verb -> RETAIN; C2b: verb live-final (छ/न, R6.3b) -> RETAIN
  (भन्छ/सुत्छ/हुन्छ/भएन override corpus GT)
- C3: function word -> RETAIN
- C4: tatsama -> RETAIN (except TATSAMA_DELETE: देश=desh)
- C5: foreign -> DONOR pronunciation (पार्क/स्कुल/किताब -> DELETE)
- C-HALO: a SINGLE live consonant (म/त/क/स...) -> RETAIN inherent /a/
  (ma/Ta/ka/sa). General rule, no exceptions; subsumes former म lexicon entry.
- C5b: aspirated-final — native word ending in an aspirated stop/affricate
  (ख/घ/छ/झ/ठ/ढ/थ/ध/फ/भ) -> RETAIN inherent /a/ (दुख->dukha, सुख->sukha).
  Phonotactic class rule, subsumes former दुख/सुख lexicon entries.
- C6: DEFAULT native live-final noun/adj -> **DELETE** (see §3D exceptions)

### R7 — compound / sandhi
- Join schwa drops at stem+postposition (नेपाल+को->nepalko) and stem+stem
  (प्रधान+मन्त्री->pradhanmantri). Postpositions keep their own final अ.

## 3. THIS SESSION'S FIXES (2026-07-18) — all GREEN

### A) Conjunct second member keeps inherent /a/  (RULE, not exception)
`त्र=tra प्र=pra क्र=kra द्र=dra श्र=shra ब्र=bra ग्र=gra स्त=sta स्म=sma
क्ष=ksha ज्ञ=gy स्त्र=stra` (stacked conjunct).
Matra right after conjunct REPLACES the second C's /a/: त्र+ई->tri, प्र+े->pre.

### B) Au-kar ौ -> /au/  (was wrongly /o/)
सम्झौता -> samjhauta.

### C) C6 default = DELETE, curated RETAIN exceptions
Default DELETE matches native ear for short nouns (nepal, ghar, pariwar,
buddhiman, udyog, nirman, arthik, samajik, gayak, nartak, prem, kawita).
RETAIN_FINAL set: यस, कमल, पुस्तकालय, अर्थशास्त्र, मित्रता, साहित्य.

### D) Exception sets (in u5_reference.py)
- HALANTA_FINAL (DELETE): नेपाल, प्रधान, घर
- TATSAMA_DELETE (DELETE): देश -> desh
- RETAIN_FINAL (RETAIN): यस, कमल, पुस्तकालय, अर्थशास्त्र, मित्रता, साहित्य
- Foreign (C5, DELETE): पार्क->park, स्कुल->school, किताब->kitab

### E) Verb-suffix detector hardened
No longer mis-tags conjunct-final nouns (अर्थशास्त्र ends in त्र=त्+र, NOT a
verb). Only न्+छ/त्+छ and एन/ऐन negatives are verbs.

### F) Lexicon honors stored retain for token generation
पार्क/देश/स्कुल now produce correct DELETE tokens via curated entries.

### G) Curated lexicon additions (authoritative tokens)
प्रधानमन्त्री=pradhanmantri, घर=ghar, स्कुल=school, कमल=kamal,
पुस्तकालय=pustakalaya, अर्थशास्त्र=arthashastra, मित्रता=mitrata,
साहित्य=sahitya, सफलता=saphalta (medial ल schwa deleted),
काठमान्डु=kathmandu (native spelling मान्डु; काठमाडौं is Sanskritized variant).

## 4. VERIFIED WORD READINGS (plain letters, user-confirmed)

nepal, kathamandu, widyarthi, sahitya, pustakalaya, pradhanmantri,
arthashastra, deshbhakti, swatantra, wigyana, itihas, pariwar, samasya,
saphalta, awashyak, mitrata, buddhiman, swasthya, udyog, prakriti,
wyawastha, sanskriti, nirman, arthik, rajaniti, samajik, prem, kawita,
gayak, nartak, widwan, krishi, samjhauta, shiksha,
ma, dukha, sukha, yus, usle, sarkar, destira, chiniya, unline, hidnu,
bhanchha, sutchha, bhaena, hunchha, skandha, manch, gyana, kshama,
shrama, drawya, graama, brahmana, grantha, mantri, kamala, phal, bal,
pal, sal, chamal, kun, tar, sar, park, school, kitab, desh.

## 5. OPEN ITEMS / NEXT STEPS (when we resume)

1. **Expand native review** to more corpus words to find more gaps
   (stratified sample across rule types).
2. **Medial schwa rules**: सफलता (medial ल drops) is curated; consider a
   generalized medial-ल deletion rule if more examples appear.
3. **Regenerate t6_review.txt / t6_rules.txt** with final outputs.
4. **Git init + tag v0.1.0 + push to GitHub** (repo is NOT yet a git repo).
5. **Stem-splitter** for compounds (प्रधानमन्त्री currently curated; a known-
   stem dictionary would generalize compound-join handling).
6. **R7-general medial cluster** inventory: only fricative+stop currently
   (श/ष+stop). Monitor for other medial clusters.
7. Document remaining known curated-exception words in SPEC appendix.

## 5b. FIX LOG (2026-07-19) — R7 compound-join + घर reclassification

- **Bug found via TTS listening (user authority)**: `साउनलाई` produced
  `saunalai` (extra schwa) but correct is **`saunlai`**. User clarified the
  issue is the JOIN: `साउन` = `saun` (न halanta-final, drops अ), then `लाई` =
  `lai`; the segmenter was re-inserting ल's inherent अ at the join
  (saun-**a**-lai).
- **Root cause**: `लाई` was missing from `_POSTPOSITIONS`, so R7 never fired
  for it. Also the join-schwa deletion was previously applied UNCONDITIONALLY,
  which wrongly stripped the host's kept final अ (e.g. `मलाई`→`mlai` instead of
  `malai`).
- **Fix (principled R7)**: the host's final inherent /a/ is deleted at the join
  ONLY when the host, pronounced standalone, drops its final schwa per U5 —
  i.e. it is halanta-final (नेपाल→nepal, साउन→saun, करण→karan, प्रधान→pradhan).
  If the host KEEPS its final अ (म→ma, घर→ghar, यस→yas, काठमान्डु→kathamandu,
  हामी→hami), that अ is retained at the join. A single live consonant host
  (म) always keeps its अ regardless of the C6 default.
- **Latent categorization bug fixed**: `घर` was in `HALANTA_FINAL` (DELETE),
  but it is pronounced WITH final अ (`ghar`), confirmed by `घरलाई`→`gharlai`.
  Moved `घर` to `RETAIN_FINAL` in `u5_reference.py` + lexicon (C6-R, retain=True;
  tokens unchanged `['gh','a','r']`).
- **Files changed**: `nspc/core/rules.py` (added `लाई` to `_POSTPOSITIONS`;
  rewrote host-join logic to use U5 + consonant-count), `nspc/core/u5_reference.py`
  (घर moved HALANTA_FINAL→RETAIN_FINAL), `nspc/core/lexicon.py` (घर C6-H→C6-R),
  `tests/test_standard_regression.py` + `docs/SPECIFICATION.md` (घर expectation
  updated C6-H/False → C6-R/True).
- **Verified (TTS listening)**: `साउनमा`→saunma, `साउनलाई`→saunlai both correct.
- **Regression suite**: `करणबाट`→karanbata restored; `मलाई`→malai, `घरलाई`→gharlai
  correct. All 4 suites GREEN (test_native_audit 29, test_no_trailing_schwa,
  test_standard_regression, test_matra_inventory_consistency).

## 5c. FIX LOG (2026-07-19) — ँ vs ं nasal rules split

- **User correction (native ear)**: ँ (chandrabindu) and ं (anusvara) are
  DIFFERENT and must be handled by separate rules.
  - ँ (chandrabindu) = PURE vowel nasalization, न silent. सँगै → **sagai**
    (सँ = sa~ nasal-colored, गै = gai). Confirmed by user.
  - ं (anusvara) = realized as a NASAL CONSONANT matching the place of the
    FOLLOWING consonant (Sanskrit anunasika sandhi). Confirmed by user:
    संगीत → **sangit** (ं→ng before ग), संस्कृति → **sanskriti** (ं→n before स).
- **Old behaviour (wrong)**: both ँ and ं just added `~` to the vowel
  (संगीत → "sa~git", losing the ng/n consonant). Now fixed.
- **New rule (rules.py, step 5)**:
  - CHANDRABINDU → nasalize preceding vowel (`a~` etc.); no consonant.
  - ANUSVARA → insert nasal consonant by place of next consonant:
    velar(कखगघङ)→`ng`, palatal(चछजझञ)→`ny`, retroflex(टठडढण)→`N`,
    dental(तथदधन)→`n`, labial(पफबभम)→`m`, semi/sibilant/h→`n`.
    Helper `_next_consonant_token` skips virama/matra; `_ANUSVARA_NASAL` map.
- **Verified**: सँग→sag, संग→sang, परिक्षासँग→parikshasag, गञ्जसँग→ganjsag
  (ं→ny before ज), संभव→sambhaw (ं→m before भ), आँखा→a~kha (आँ=a:~).
- **Corpus scan**: 94/672 unique words carry a nasal mark; 81 emit ng/ny/~.
  No broken patterns. All 4 suites remain GREEN.
- **Files changed**: `nspc/core/rules.py` (split nasal handlers, `_ANUSVARA_NASAL`,
  `_next_consonant_token` helper).

## 5e. FIX LOG (2026-07-19) — घर/कमल reclassified to HALANTA_FINAL

- **Native correction**: घर -> **ghar** and कमल -> **kamal** — both DROP their
  final inherent /a/ (halanta-final), NOT retain. साहित्य -> **sahitya** KEEPS
  its final अ (confirmed: final schwa NOT dropped). सा = "saa" (long आ), so
  साहित्य = sahitya with long initial आ — the rule is correct, no change there.
- **Bug found**: a prior fix (5b) had wrongly moved घर into RETAIN_FINAL, making
  the pure rule emit "ghara". Same class of error for कमल ("kamala"). The
  lexicon overrides were masking it.
- **Fix**: moved घर and कमल from `RETAIN_FINAL` -> `HALANTA_FINAL` (U5 C6-H,
  DELETE). Deleted their now-redundant lexicon curated overrides. Verified via
  rule path: घर->ghar, कमल->kamal (src=rule). Updated
  `test_standard_regression.py` expectation (घर C6-H/False) and SPECIFICATION
  exception-set listing. साहित्य stays in RETAIN_FINAL (keeps final अ).
- All 4 suites GREEN.

## 5d. FIX LOG (2026-07-19) — सँग final अ + foreign-name medial अ

- **User correction (native ear)**:
  1. `सँग` (सम्बन्धवाचक / postposition, never standalone) -> **saga**, NOT
     "sag". The final inherent /a/ of ग is RETAINED. Consistently:
     घरसँग->gharasaga, नेपालसँग->nepalsaga, मसँग->masaga, हामीसँग->hamisaga.
  2. `शकिरा` (foreign name, Shakira) -> **shakira**, NOT "shkira". The initial
     श must keep its inherent /a/ (sha), because it is NOT a native onset cluster.
- **Root causes**:
  - Final-अ: postpositions were subject to the C6 final-schwa DELETE like bare
    nouns. Fixed by exempting postpositions (`is_postposition` flag in segment):
    a postposition keeps its final inherent /a/.
  - Medial-अ: `_medial_cluster` had a BLANKET rule "fricative(श/ष)+stop -> drop
    first's अ". This wrongly deleted श's अ in शकिरा (श+क medial). Native words
    do NOT rely on this: their fricatives (आकाश, देश, विकास...) are HOST-FINAL
    (handled by the host-final path, not medial), and conjuncts use an explicit
    virama (स्क=स्+क, handled by CLUSTER_MAP). So the blanket rule was dead
    weight for natives and harmful for foreign names.
- **Fix**: `_medial_cluster` now returns False (conjuncts via virama/CLUSTER_MAP
  only). `is_postposition` (word in/_POSTPOS_SET or ends with one) exempts the
  final-schwa DELETE. Verified: शकिरा->shakira; the 30 corpus fricative+postposition
  words (आकाशको, देशबाट, विकासजस्तै...) are UNCHANGED. All 4 suites GREEN.
- **Foreign/loan-word finalization deferred**: user wants a rule-based foreign
  detection (not word lists). Tabled for a later session; शकिरा fixed via the
  corrected medial-cluster rule (it is not a native conjunct), not via a lexicon
  entry.
- **Files changed**: `nspc/core/rules.py` (`_medial_cluster`→False; `is_postposition`
  flag + final-अ exemption).

## 6. KNOWN LIMITATIONS

- Final schwa is partially idiosyncratic in Nepali; handled via C6 default +
  curated exception sets rather than a pure orthographic rule.
- Compounds handled by curation until a stem-splitter exists.
- व = "w" vs "b" is context-dependent (विद्वान्=widwan, कविता=kawita); no
  general rule yet — handled per word.
- Corpus (7282 rows = 942 unique words) GT is self-consistent but wrong vs
  native ear on final schwa / conjuncts; kit overrides it.

## 7. TEST COMMANDS (run from repo root)

```
py tests/test_native_audit.py
py tests/test_no_trailing_schwa.py
py tests/test_standard_regression.py
py tests/test_matra_inventory_consistency.py
```
All four must stay GREEN. The regression .py files are standalone scripts
(call sys.exit), NOT pytest-collectable modules.

## 8. QUICK DEMO

```
py -c "from nspc.core import lexicon as L; print(L.process('प्रधानमन्त्री'))"
# -> (['p','r','a','Dh','a','N','m','a','N','t','r','i:'], ..., 'pradhanmantri')
```

## 5b. LEXICON PRUNING + SEED-GT OVERRIDE (2026-07-19) — all GREEN

### Goal
Shrink the curated lexicon to ONLY genuine irregularities; make the rule engine
the authority over unreliable corpus GT.

### Outcome
- **15 redundant curated overrides deleted** (rule already produced correct
  output): देश, भन्छ, सुत्छ, हुन्छ, भएन, देशतिर, स्कन्ध, स्कुल (8 BUCKET-1) +
  पुस्तकालय, अर्थशास्त्र, मित्रता, साहित्य, सफलता, प्रधानमन्त्री, चिनियाँ
  (7 matra-length — native confirmed ा is ALWAYS LONG, lexicon short forms were
  deviations).
- **12 curated entries kept** as genuine irregularities (updated: म dropped via
  C-HALO, दुख/सुख dropped via C5b — now **9**: पार्क, विकास, यस, उसले, सरकार,
  मञ्च, अनलाइन, हिँड्न, काठमान्डु).
- **Seed GT override fix**: `L.process` now routes seed-only entries to the PURE
  RULE (ignoring the seed's unreliable branch/retain from corpus GT). Only
  curated entries override the rule. This exposed + fixed 3 latent seed errors
  that curated deletes had been masking: भन्छ→bhaNcha, सुत्छ→suTcha (C2b verb
  retain), स्कन्ध→skaNDha (C1 conjunct retain). All three now resolve via rule.

### Verification
- All 4 suites GREEN. test_native_audit updated: चिनियाँ now expects rule output
  `ciNiya:` (याँ = long nasal a:~, per native: या is LONG).
- Spot checks: देश→Desh, स्कुल→skul, पुस्तकालय→pusTaka:laya, साहित्य→sa:hiTya,
  भन्छ→bhaNcha, स्कन्ध→skaNDha (all src=rule).
- Commit 8a730e1 pushed to GitHub (private: ansipd/nepali-speech-phones-kit).

### Remaining rule-based opportunities (future)
1. दुख/सुख → RETAIN_FINAL class.
2. मञ्च → ञ→n assimilation rule.
3. उसले/सरकार/अनलाइन → medial schwa-deletion-after-स/र pattern.
4. पार्क → foreign-loan detection (tabled).

### 5c. SINGLE-CONSONANT HALO RULE (2026-07-19) — all GREEN
- New U5 branch `C-HALO`: a word of exactly one live consonant with no
  matra/virama (म, त, क, स...) always retains inherent /a/ (ma, Ta, ka, sa).
  Implemented via `normalize.is_halo()` → `auto_tag` `halo` tag → U5 C-HALO
  RETAIN. This is the most general form of the R7 comment "म -> ma".
- Deleted the curated `म -> ma` override (now rule-derived). Lexicon now 11
  genuine irregularities.
- Verification: म/त/क/स/न/र/य/ह/व/ल/प all -> ...a via rule (src=rule).
  All 4 suites GREEN.

### 5d. ASPIRATED-FINAL RETAIN RULE (C5b) (2026-07-19) — all GREEN
- New U5 branch `C5b`: native word whose FINAL consonant is an aspirated
  stop/affricate (ख/घ/छ/झ/ठ/ढ/थ/ध/फ/भ) RETAINs inherent /a/ (breathy release
  realized with a following vowel). Phonotactic class rule, NOT a word list.
  Implemented via `_final_consonant_base(orth) in _ASPIRATED` in u5_reference.
- Deleted the curated दुख/सुख overrides (now rule-derived). Lexicon now 9
  genuine irregularities. test_native_audit updated: दुख->Dukha (द = dental D),
  सुख->sukha, branch C5b.
- Verification: All 4 suites GREEN.

### 5e. NASAL SPLIT REGRESSION TEST (R3.4) (2026-07-19)
- Added `tests/test_nasal_anusvara_chandrabindu.py` (standalone, 9 cases) to
  LOCK IN the ँ (chandrabindu = vowel nasalization only) vs ं (anusvara =
  homorganic nasal consonant by following consonant) split. Confirms the OLD
  bug (treating both identically by nasalizing the vowel) cannot regress:
  संगीत->sanggi:T, संभव->sambhaw, संस्कृति->sanskrTi, संज्ञ->sanygy, हंस->hans,
  कंठ->kaNtha, पंख->pangkha, सँग->saga, सँगै->sage. All GREEN.
- Confirmed by native review: संस्कृति phonetically "sanskriti" (nasal consonant
  before स), so the nasal-consonant realization is correct, not vowel nasalization.

### 5f. JOINT REVIEW OF THE 9 CURATED ENTRIES (2026-07-19)
Reviewed each of the 9 remaining curated entries with the native speaker:
- **यस**: yus/yas/yes all sound identical -> curated `yus` KEPT, no change.
- **मञ्च / मंच**: confirmed SAME word (anusvara vs conjunct spelling). Added
  `normalize._SPELLING_VARIANTS` mapping मंच -> मञ्च, applied in both
  `rules.segment` and `lexicon.process` via `canonicalize()`. Both yield "manch"
  through the rule (no separate lexicon entry for मंच).
- **उसले**: productive pronoun+ले pattern (उस/यस/जस/कस/उन/त्यस/कुन + ले).
  FIXED via R7 join rule: changed `host_drops_final_a` from
  `(not retain) and (host_cons>1 or virama)` to simply `not _host_retain`, so
  ANY host that deletes its final schwa standalone (including monosyllabic
  उस/कस/जस/उन ending in स/न) drops it at the join. Now उसले->usle, जसले->jasle,
  कसले->kasle, उनले->uNle, त्यसले->Tyasle, कुनले->kuNle — all rule-derived.
  Verified ZERO corpus postposition words remain lexicon-sourced. Override
  DELETED; lexicon now 8 entries.
- **सरकार**: सर+कार compound, र's final अ drops. Word-specific (no safe general
  rule without a stem-splitter) -> KEPT curated.
- **विकास, अनलाइन, हिँड्न, काठमान्डु, पार्क**: confirmed KEPT curated.
- Net code change: मंच->मञ्च map + R7 host_drops fix. Lexicon now 8 genuine
  irregularities. All 5 suites GREEN. Not yet committed (pending push).

