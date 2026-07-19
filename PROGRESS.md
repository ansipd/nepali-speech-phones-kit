# PROGRESS LOG — Nepali Speech Phones Kit (NSPC-Kit)

**Project**: Deterministic, citable Nepali pronunciation Standard v1.0 + universal
engine-agnostic G2P frontend for TTS training (no trained voice).
**Location**: `C:\Users\Sandip Ghimire\nepali-speech-phones-kit\`
**Status**: All 4 test suites GREEN as of 2026-07-19. Resting.

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
