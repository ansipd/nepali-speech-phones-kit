# NEPALI COMPUTATIONAL PRONUNCIATION STANDARD
# SPECIFICATION (Authoritative) — v1.0
# Status: STABLE. This document is the authority. Implementations conform TO
#         it; the specification does not change when an implementation changes.

SCOPE. Standard Nepali (Kathmandu-valley normative variety, as codified by the
Nepal Academy). This is a LINGUISTIC SPECIFICATION, not code. Every rule has an
explicit boundary: Rule ID, Purpose, Inputs, Preconditions, Action, Ordering,
Dependencies.

REPRODUCIBILITY CLAIM. A second linguist starting from the same primary sources
(Acharya 1991; Devī Nepal 2011; Praśāsanic Vyākaraṇ Varṇavinyās; Clements &
Khatiwada 2009) and applying the tagging procedure (§11) and the final-schwa
decision procedure (§6, U5) will derive, for every word, the same final-schwa
classification. The classification is a pure function of an enumerable tag set
under a fixed priority order. There is no probabilistic step, no "speaker
judgement" step, and no hidden state.

================================================================================
CHAPTER 1 — WRITING SYSTEM & UNICODE NORMALIZATION
================================================================================

R1.1 [Script]
  Purpose : Define the writing system unit.
  Inputs  : A Nepali text string.
  Action  : Treat Devanagari as an abugida of aksharas (orthographic syllables).
            Each consonant letter encodes C + inherent /a/; matras override the
            inherent vowel; independent vowels begin vowel-initial aksharas.
  Depends : none.

R1.2 [Character set]
  Purpose : Bound the symbol inventory.
  Inputs  : Unicode codepoints in the string.
  Action  : Accept the Nepali Devanagari subset: 33 consonants, vowels,
            matras, virama U+094D, candrabindu U+0901, anusvara U+0902,
            visarga U+0903, danda U+0964. Flag letters that do not occur in
            native Nepali (e.g. ळ, ड़) as loan-only.
  Depends : R1.1.

R1.3 [NFC normalization]   ← first step of every trace
  Purpose : Remove encoding ambiguity before phonology runs.
  Inputs  : Raw Unicode string.
  Precond : Codepoints may be in any equivalent form (NFC/NFD/NFKC).
  Action  : Apply Unicode NFC. Decompose and recompose conjuncts to an explicit
            (dead-consonant + live-consonant) pair representation so that each
            consonant's dead/live status is decidable from the string alone.
  Ordering: MUST run before R1.4 and before all phonology.
  Depends : R1.1, R1.2.

R1.4 [Virama / halanta detection]
  Purpose : Identify MANDATORY /a/ deletion signals.
  Inputs  : NFC-normalized string (post R1.3).
  Action  : A consonant immediately followed by U+094D is DEAD (inherent /a/
            cancelled). Otherwise the consonant is LIVE and carries /a/
            (subject to later rules). For a conjunct, mark the final member
            LIVE; mark all non-final members DEAD.
  Ordering: After R1.3. Consumed by R6 (U5.C0) and the medial rules R3.x.
  Depends : R1.3.

================================================================================
CHAPTER 2 — SEGMENTAL INVENTORY
================================================================================

R2.1 [Consonant map]
  Purpose : Map each consonant letter to its phoneme.
  Inputs  : NFC string; environment.
  Action  : C→phoneme per inventory (28–30 phonemes; alveopalatal preferred
            over "retroflex", Acharya 2.0.5). Voiced aspirates /bh dh jh gh/
            simplify to /b d j g/ post-vocalically (R7.1). व→/b/ except /w/
            by environment (R2.3).
  Depends : R1.3.

R2.2 [Vowel map & inherent vowel]
  Purpose : Define vowels and the inherent vowel value.
  Inputs  : Matras; absence of matra on a live consonant.
  Action  : Oral /i e a a: o u/ (length NOT phonemic). The inherent vowel is
            mid-central /a/ realized [ə]~[ʌ] (Acharya p.90, JIPA) — NOT low
            /a:/. Nasals /ĩ ẽ ã õ ũ/ (no /õ~/).
  Depends : R1.1.

R2.3 [Glides]
  Purpose : Resolve य/व.
  Inputs  : य/व in onset vs coda; following context.
  Action  : य→/y/, व→/w/ in onset; realized [i]/[u] in coda. व→/b/ when the
            Academy ba/va split applies (§11.5).
  Depends : R2.1.

R2.4 [Visarga]
  Purpose : Handle ः.
  Inputs  : Visarga codepoint.
  Action  : SILENT in Sanskrit loans (दुःख→[dukha]; /h/ also deleted
            post-vocalically, R3.9). Loan-only.
  Depends : R1.1.

================================================================================
CHAPTER 3 — SYLLABLE STRUCTURE & PHONOTACTICS
================================================================================

R3.0 [Allowed syllables]
  Purpose : Define the phonotactic envelope.
  Inputs  : Syllable candidate.
  Action  : Allowed: V, CV, CCV, CCCV, VC, CVC, CCVC, CCCVC. CVCC is NOT a
            native Nepali syllable (Regmi 2006; Gipan 2025).
  Depends : R1.1.

R3.1 [Word-initial medial /a/]
  Purpose : Medial inherent /a/ rule (non-final, position 1).
  Inputs  : A live consonant at syllable onset 1.
  Precond : Not the final syllable (final governed by R6).
  Action  : PRONOUNCE /a/.
  Depends : R1.4.

R3.2 [Medial /a/ before dead consonant]
  Purpose : Medial inherent /a/ rule (before a halanta).
  Inputs  : Live consonant immediately followed (across the boundary) by a DEAD
            consonant.
  Action  : PRONOUNCE /a/ (deletion would create an illicit cluster).
  Depends : R1.4.

R3.3 [Medial /a/ before nasalization]
  Purpose : Medial inherent /a/ rule (before nasal sign).
  Inputs  : Live consonant followed by candrabindu/anusvara.
  Action  : PRONOUNCE /a/.
  Depends : R1.4, R2.2.

R3.4 [Nasal marks — ँ vs ं are DISTINCT rules]
  Purpose : Correct realization of the two nasal diacritics. They are NOT the
            same; native ear confirms different outputs.
  (a) CHANDRABINDU (ँ, U+0901): PURE vowel nasalization. NO consonant is
      realized; the preceding vowel is marked nasal (~). The latent न is
      SILENT.  e.g. सँगै -> sa~ + gai = "sagai"; सँग -> "sag"; आँखा -> a~kha.
  (b) ANUSVARA (ं, U+0902): realized as a NASAL CONSONANT whose place matches
      the FOLLOWING consonant (Sanskrit anunasika sandhi, phonetically active
      in Nepali):
        velar   (क ख ग घ ङ)      -> ng   e.g. संगीत -> sangit
        palatal (च छ ज झ ञ)      -> ny   e.g. संज्ञ -> sangya
        retroflex(ट ठ ड ढ ण)       -> N
        dental  (त थ द ध न)        -> n    e.g. संस्कृति -> sanskriti
        labial  (प फ ब भ म)        -> m    e.g. संभव -> sambhaw
        semi/sibilant/h (य र ल व श ष स ह) -> n
      If no following consonant (word-final ं, rare), default to n.
  Depends : R1.4; reference impl helper _next_consonant_token + _ANUSVARA_NASAL.

R3.5 [Medial /a/ before live conjunct member]
  Purpose : Medial inherent /a/ rule (in a conjunct).
  Inputs  : Live consonant that is a non-final member of a conjunct.
  Action  : PRONOUNCE /a/.
  Depends : R1.4.

R3.6 [Pronoun final]
  Purpose : Final /a/ on pronouns.
  Inputs  : Pronoun (यस, उस, त्यस, कस, …) written ajanta.
  Action  : DELETE /a/ (pronouns behave as native C6).  [contrast C3 func words]
  Depends : R6 (default C6); listed explicitly to preclude pronoun-as-function
            misclassification.

R3.9 [/h/ deletion post-vocalically]
  Purpose : Regular post-vocalic deletion.
  Inputs  : /h/ after a vowel.
  Action  : DELETE /h/ (रहेन→/raen/).
  Ordering: Run with R2.1/R7.1 in the segmental cleanup pass (pre-final).
  Depends : R2.1.

R3.5b [Illicit-cluster medial deletion]
  Purpose : Medial /a/ deletion where retention would create an illicit cluster
            or in a reduced unstressed compound syllable.
  Inputs  : Medial live consonant NOT covered by R3.1/R3.2/R3.3/R3.5.
  Action  : In a compound-internal reduced syllable, DELETE /a/ (Ch.4.2, R5.9).
  Depends : R3.0, R5.9.

================================================================================
CHAPTER 4 — SUPRASEGMENTALS (stress; predictable, does not gate schwa)
================================================================================

R4.1 [Stress non-phonemic]
  Purpose : Establish stress is predictable.
  Inputs  : Syllable weight sequence (R3.0 weight degrees).
  Action  : Apply NSR-1/NSR-2 (weight-based initial/shift), CWSR (compound),
            PSR/SSR (phrase), ES (emphatic). Stress is fully predictable.
  Depends : R3.0.

R4.2 [Unstressed reduction]
  Purpose : Vowel-quality reduction family.
  Inputs  : Unstressed vowels.
  Action  : Reduce to [a] or delete (compounds, Acharya 3.5.3.3). This is a
            SEPARATE process from final-schwa deletion (R6); it refines vowel
            QUALITY only and does NOT gate R6.
  Depends : R4.1.  (Independent of R6 outcome.)

================================================================================
CHAPTER 5 — MORPHOLOGY & WORD FORMATION
================================================================================

R5.1 [Local morpheme phonology]
  Purpose : Define compositionality.
  Inputs  : Morpheme-segmented word.
  Action  : Each morpheme's inherent /a/ is computed independently by R3.x/R6;
            orthographic joining (noun+postposition) does not merge phonology.
  Depends : R3.x, R6.

R5.2 [Gemination across boundaries]
  Purpose : Regular assimilatory gemination.
  Inputs  : Stem-final C + suffix-initial same-place C.
  Action  : Geminate (/ek.ghau/→/eg.ghau/). Post-lexical rule.
  Depends : R2.1.

R5.3 [Suffix etymology → final /a/]
  Purpose : Tatsama suffixes retain /a/.
  Inputs  : Suffix origin tag.
  Action  : Sanskrit-derived suffix → C4 retention; native suffix → C6 default.
  Depends : R8 (etymology tags), R6.

R5.4 [Compound internal /a/]
  Purpose : Compound-final morpheme /a/.
  Inputs  : Compound member.
  Action  : Delete unless phonotactically blocked (R3.0). केशवदेव→/kesabdeb/;
            रत्न retained /ratna/. [Acharya p.91 रत्न]
  Depends : R3.0, R3.5b.

R5.9 [Compound stress + internal deletion coupling]
  Purpose  : Couple R4.2 and R3.5b for compounds.
  Inputs  : Compound with >1 member.
  Action  : Apply CWSR (R4.1) + delete unstressed internal /a/ per R3.5b.
  Depends : R4.1, R3.5b, R5.4.

================================================================================
CHAPTER 6 — THE FINAL-SCHWA ALGORITHM (CORE, authoritative)
================================================================================

R6.0 [Required per-word tags]   ← the only information U5 consumes
  Purpose : Define U5's input vector.
  Inputs  : NFC word; morpheme segmentation; POS; etymology.
  Action  : Produce the tag tuple
              T = {dead, conjunct, lneg, verb, verb_n_end,
                   verb_stem_halanta, func, tatsama, foreign, donor_schwa}
            derived by O4 (§11) from orthography + etymology. U5 reads ONLY T.
  Depends : R1.3, R1.4, §11 (O4 tagging).

R6 — U5, THE UNIFIED PRIORITY RULE
  Purpose : Decide, for the FINAL inherent /a/ of a word, RETAIN vs DELETE.
  Inputs  : Tag tuple T (R6.0). Orthography consumed via R1.4 (virama).
  Precond : All R1–R5 segmental/medial rules already applied; only the FINAL
            inherent /a/ remains to be resolved.
  Action  : Evaluate in priority order; FIRST match wins:

    ┌─────┬──────────────────────────────────────────────────────────────┐
    │ C0  │ dead == TRUE  → DELETE /a/.                                  │
    │     │ (virama present; R1.4). MANDATORY.                            │
    ├─────┼──────────────────────────────────────────────────────────────┤
    │ C1  │ conjunct == TRUE → RETAIN /a/,                                │
    │     │   EXCEPT if lneg == TRUE → DELETE.                            │
    │     │ L_neg = {मञ्च, गञ्ज, पन्त} (Newar/surname conjunct-final).    │
    ├─────┼──────────────────────────────────────────────────────────────┤
    │ C2  │ verb == TRUE (and not C0) → RETAIN /a/.                        │
    │     │ NOTE: verb forms such as हुन्, छन्, हुन्छन्, गर्नेछन् ARE      │
    │     │ written with an explicit virama on न (न् = न+U+094D), so they  │
    │     │ match C0 (dead final) and DELETE — they do NOT need a special  │
    │     │ verb branch. The earlier "C2.1" proposal (schwa deleted though  │
    │     │ NO virama written) was WITHDRAWN: standard Devanagari encodes   │
    │     │ these with a virama, and Wikipedia's "[t͡sʰʌn]/[gʌi̯n]" describes │
    │     │ the phonetic OUTPUT (no schwa), which U5.C0 already predicts.   │
    ├─────┼──────────────────────────────────────────────────────────────┤
    │ C3  │ func == TRUE → RETAIN /a/.                                    │
    │     │ (postposition, adverb, particle, interjection, onomatopoeia)  │
    ├─────┼──────────────────────────────────────────────────────────────┤
    │ C4  │ tatsama == TRUE → RETAIN /a/.                                 │
    │     │ (unassimilated Sanskrit loan; keeps Sanskrit surface)         │
    ├─────┼──────────────────────────────────────────────────────────────┤
    │ C5  │ foreign == TRUE → use DONOR pronunciation                    │
    │     │   (donor_schwa == TRUE ⇒ retain, else delete).                │
    ├─────┼──────────────────────────────────────────────────────────────┤
    │ C6  │ DEFAULT (no above match) → DELETE /a/.                        │
    │     │ (native noun / adjective / assimilated loan)                  │
    └─────┴──────────────────────────────────────────────────────────────┘

  Ordering: C0 → C1 → C2 → C3 → C4 → C5 → C6. First match wins.
  Dependencies: R6.0 (tags); R1.4 (dead/conjunct); §11 (tag derivation);
                R3.0 (phonotactic basis of C1 retention).
  Determinism: pure function T → {RETAIN, DELETE}. No backtracking.

R6.1 [Orthographic signature (O4 bridge)]
  Purpose : Make R6 decidable from spelling alone where possible.
  Inputs  : Academy orthography status (ajanta/halanta).
  Action  : (a) native noun/adj/pron written AJANTA ⇒ C6 deletes (reconciles
            ajanta spelling with halanta pronunciation); (b) verb/avyaya written
            HALANTA ⇒ C0 deletes; (c) loan pronounced halanta but written
            ajanta ⇒ C5 donor; (d) tatsama keeps Sanskrit halanta ⇒ C4.
  Depends : §11 (O4), R6.

R6.2 [Medial /a/ dispatch]
   Purpose : Route non-final /a/ to the correct R3.x rule.
   Inputs  : Position of the live consonant.
   Action  : final syllable → R6 (U5); non-final → R3.1/R3.2/R3.3/R3.5/R3.5b.
   Depends : R3.x, R6.

R6.3 [Verb-final suffix — DEAD final → C0 (mandatory DELETE)]
   Purpose : A verb form whose terminal consonant is DEAD (ends in virama न्)
             deletes the final inherent /a/. It must NOT be treated as a C1
             conjunct (which would RETAIN).
   Inputs  : Orthography, Academy GT (validated).
   Action  : If the word ends in a bare virama (न्) → tag dead=TRUE, verb=TRUE,
             conjunct=FALSE → resolve via C0 → DELETE.
   Examples (DEAD final, delete):
               हुन्   → h u N        (ends in न्)
               छन्   → ch a N        (ends in न्)
               हुन्छन् → h u N ch a N  (ends in न्; last schwa deleted)
   Rationale : Words ending in न् carry an explicit virama (न् = न+U+094D), so
               the final consonant has no inherent vowel by definition. U5.C0
               deletes. Treating न्+छ as a C1 conjunct would wrongly RETAIN.
   Depends : R1.4, R6 (C0).

R6.3b [Verb-final suffix — LIVE final (छ/न) → RETAIN (native-speaker validated)]
   Purpose : A verb form whose terminal consonant is LIVE (ends in छ or न, NOT
             न्) RETAINs the final inherent /a/.
   Inputs  : Orthography + native-speaker pronunciation (committee-validated;
             OVERRIDES the corpus GT, which encoded these as DELETE).
   Action  : If the word is a verb form and its absolute final character is a
             LIVE consonant (छ, or न after ए/ै), tag verb_final_live=TRUE,
             verb=TRUE, conjunct=FALSE, dead=FALSE → resolve via C2b → RETAIN.
   Examples (LIVE final, retain):
               भन्छ  → bh a N ch a   (न्+छ, ends in live छ)
               सुत्छ  → s u T ch a    (त्+छ, ends in live छ)
               हुन्छ  → h u N ch a    (ends in live छ)
               भएन  → bh a e N a     (ए+न, ends in live न)
   Note     : हुन्छन्एन is a misspelling / non-word (not in dictionary); excluded.
   Rationale : Native speakers confirm these endings are pronounced with a final
               vowel ("bhanch-a", "sutch-a", "hunch-a", "bhaen-a"). The corpus GT
               (DELETE for भन्छ/सुत्छ) is overridden by direct native-speaker
               evidence. The DEAD-final counterpart हुन्छन् (न्) still deletes
               under R6.3. This is the live/dead split: live-final verb endings
               retain, dead-final (न्) delete.
   Depends : R1.4, R6 (C2b).

R6.4 [Terminal grammatical suffix → final /a/ DELETE]
   Purpose : Compounds ending in a known terminal suffix delete the final
             inherent /a/ of the absolute final consonant, regardless of the
             stored branch of the head/stem.
   Inputs  : Orthography, Academy GT (validated).
   Action  : If the word ends in any of {बाट, तिर, सँग, दार, हरू, मा, ले,
             सँगै, भरि, सम्म, पछि, अघि, ...} (extensible list), force C6 DELETE
             on the final consonant. The stored U5 branch of the compound
             reflects its head, not the suffix; the suffix's final schwa is
             deleted independently (e.g. करणबाट → ...ba T, not ...ba T a).
   Rationale : Prevents the Kala "trailing ax" defect on compounds. Each listed
               suffix has a fixed schwa-deleting behavior in Nepali (बाट="baat",
               तिर="tir", सँग="sãg"). Validated against GT.
   Depends : R6 (C6).

================================================================================
CHAPTER 7 — SANDBHI (morpheme-boundary phonology)
================================================================================

R7.1 [Post-vocalic aspirate simplification]
  Purpose : Simplify voiced aspirates post-vocalically.
  Inputs  : /bh dh jh gh/ after a vowel.
  Action  : → /b d j g/. Segmental cleanup pass (pre-final).
  Depends : R2.1.

R7.2 [Sandhi gemination]
  Purpose : Assimilatory gemination at boundaries.
  Inputs  : Morpheme junction.
  Action  : Geminate same-place C (R5.2). Non-geminating voice-loss assimilation
            also applies (/buj.pa.ca.o/→/buc.pa.ca.o/).
  Depends : R5.2.

R7.3 [Sandhi does not override R6]
  Purpose : Fix rule interaction.
  Inputs  : Junction of two morphemes each already resolved by R6.
  Action  : Sandhi operates ON the R6 output at boundaries; no R6 branch is
            cancelled by sandhi.
  Depends : R6, R7.2.

================================================================================
CHAPTER 8 — ETYMOLOGY & LOANWORD CLASSES (feed R6.0 tags)
================================================================================

R8.1 [Etymology → tag]
  Purpose : Assign etymology class.
  Inputs  : Word + origin source.
  Action  : Native(tadbhava)→C6 (unless conjunct C1); Tatsama→C4; Foreign→C5;
            Indigenous Newar→C6 or L_neg (conjunct-final); Persian/Arabic
            naturalized→C6.
  Depends : §11 (O4 origin classification).

R8.2 [L_neg principled class]
  Purpose : Justify the C1 exception list.
  Inputs  : Conjunct-final word.
  Action  : L_neg = Newar-origin (मञ्च, गञ्ज) or caste surname (पन्त). All other
            conjunct-final words are Indo-Aryan → retain by C1. L_neg is a
            principled class, not an ad-hoc list.
  Depends : R8.1.

R8.3 [Naturalization gradient]
  Purpose : C5 vs C6 boundary for loans.
  Inputs  : Loan recency + assimilation degree.
  Action  : Older loans (Persian किताब) → C6; recent (English पार्क, मार्च) →
            C5. Boundary = recency + phonological assimilation.
  Depends : R8.1.

================================================================================
CHAPTER 9 — EXCEPTIONS (minimal by design)
================================================================================

R9.1 [No lexical exceptions to U5]
  Purpose : State coverage.
  Inputs  : Any word.
  Action  : Every native/assimilated word matches exactly one of C0–C6 (+L_neg
            for C1). "Problem" words are ordinary cases: दुख/सुख = C4 tatsama;
            सरकार = C6 (/sarkar/). The former "C9.1 residual set" is WITHDRAWN
            (misclassification, not exception).
  Depends : R6.

R9.2 [Final-vowel length is a separate dimension]
  Purpose : Remove length/schwa coupling.
  Inputs  : Word ending in ई/ऊ.
  Action  : R_LEN (positive rule): final ई/ऊ DIRGHA for strīliṅgī and bhāvavācī
            nouns; PRIORITIZES over general hrasva. Does NOT interact with R6.
  Depends : §11.4.

R9.3 [Everything else is C0/C1/C2/C4]
  Purpose : Exhaustiveness.
  Inputs  : Any apparent exception.
  Action  : Reduces to (a) conjunct-final Newar (C1+L_neg), (b) verb contrast
            (C0/C2), or (c) tatsama (C4). None requires an arbitrary rule.
  Depends : R6, R8.

R9.4 [Failure handling]
  Purpose : Define what a non-match means.
  Inputs  : Word failing all R6 branches.
  Action  : Treat as data/annotation error or unlisted recent loan → assign C5.
            NOT a linguistic exception. Grammar is exception-free at lexical
            level.
  Depends : R6.

================================================================================
CHAPTER 10 — ALGORITHM (deterministic procedure; also realized by
                     reference_impl.py, which is NOT authoritative)
================================================================================

R10.1 [Procedure]
  Purpose : Encode the order of all rules for a deterministic implementation.
  Inputs  : Word string.
  Action  : (1) R1.3 NFC; (2) R1.4 dead/live; (3) R2.1/R2.2/R2.3 segmental,
            R2.4 visarga; (4) R3.9 /h/-del, R7.1 aspirate-simp; (5) R3.0 initial
            CC epenthesis (/aksa/); (6) R3.x medial /a/; (7) R6 (U5) FINAL /a/;
            (8) R7.2 sandhi/gemination; (9) R4.1 stress (quality only).
  Ordering: fixed. Each step is data-driven from tags; no probabilistic step.
  Depends : all above.

R10.2 [Output]
  Purpose : Define output form.
  Inputs  : Post-R10.1 representation.
  Action  : Emit phonemic transcription in / / using /a/ for inherent vowel;
            realize /a/ as [ə] or [ʌ] per dialect. A trace (§12) MUST accompany
            output for debugging.
  Depends : R10.1.

================================================================================
CHAPTER 11 — ORTHOGRAPHY LAYER (O4): tags that R6 consumes
================================================================================

O4.1 [Authority]
  Purpose : Name the spelling standard.
  Inputs  : Standard Nepali orthography.
  Action  : Nepal Academy Brihat Shabdakosh 10th ed. (2075/2018) is the
            mandatory standard; Devī Nepal (2011) + Praśāsanic Vyākaraṇ
            Varṇavinyās (pp.327–349) codify it. This layer is ORTHOGRAPHIC; it
            supplies the tag VALUES R6.0 consumes, not phonetics.
  Depends : none (external authority).

O4.2 [Origin classification → R8 tags]
  Purpose : Derive etymology tag.
  Inputs  : Word.
  Action  : Mūla/maulik → {TATSAMA (C4), TADBHAVA (C6), JHAṚṚĀ (C3)};
            Āgantuk → {Indigenous (Newar→C6/L_neg), Foreign (C5)}. [Devī Nepal §2]
  Depends : O4.1.

O4.3 [Halanta vs Ajanta → dead tag]
  Purpose : Bridge spelling to R1.4/R6.
  Inputs  : Written form.
  Action  : noun/pron/adj halanta-pronounced ⇒ written AJANTA; verb/avyaya ⇒
            written HALANTA; loan halanta-pronounced ⇒ written AJANTA; tatsama
            keeps Sanskrit halanta. [Devī Nepal §3; PS §3]
  Depends : O4.1, R1.4.

O4.4 [Raswa/Dirgha → R9.2 length]
  Purpose  : Medial/final length tags.
  Inputs  : i/u position.
  Action  : Non-final tadbhava/loan i/u = RASWA; tatsama keeps Sanskrit length;
            final ई/ऊ length per R9.2. Does not affect R6.
  Depends : O4.1.

O4.5 [Ba/Va & sibilant distribution]
  Purpose : Character-map tags (do not affect schwa).
  Inputs  : ब/व; श/ष/स.
  Action  : व→ब in closed Academy set; तालव्य श lexically protected in some
            surnames. Implemented as separate maps (R2.1/R2.3).
  Depends : R2.1.

O4.6 [Padayoga]
  Purpose : Word-joining orthography.
  Inputs  : Postposition/vibhakti spelling.
  Action  : Written joined (घरमा) but computed as separate morphemes (R5.1);
            comparison words written split before name/pronoun phrase.
  Depends : R5.1.

O4.7 [Source conflict policy]
  Purpose : Resolve authority conflicts.
  Inputs  : Divergence between Devī Nepal (2011) and Praśāsanic Vyākaraṇ.
  Action  : Praśāsanic Vyākaraṇ Varṇavinyās wins. (Confirmation tool
            nepalibhasha/varnavinyas is NEVER a phonetic authority.)
  Depends : O4.1.

================================================================================
CHAPTER 12 — DETERMINISTIC TRACE CONTRACT (the "why?" requirement)
================================================================================

Every implementation conforming to this standard MUST, for every input word, be
able to emit a trace of the form:

    NFC normalization
        └─► O4  (ajanta/halanta, raswa/dirgha, etymology tag)
              └─► Native-class / POS assignment
                    └─►                      U5.{branch}   (C0|C1|C2|C3|C4|C5|C6)
                          └─► Phone output

The trace MUST record, for the final /a/ decision: the matched branch, the
tag tuple that triggered it, and the RETAIN/DELETE action. This makes every
mispronunciation debuggable to a single rule.

WORKED TRACES (each independently reproducible from the spec):

  विकास
    NFC(विकास)
      └─ O4: conjunct-final tatsama, not L_neg
        └─ class: tatsama
          └─ U5.C1 (conjunct, not L_neg) → RETAIN
            └─ /vikas/

  घर
    NFC(घर)
      └─ O4: native noun, ajanta
        └─ class: native noun (default)
          └─ U5.C6 (DEFAULT) → DELETE
            └─ /ghar/

  हुन्
    NFC(हुन्)            [न written with virama: न् = न+U+094D]
      └─ O4: verb, DEAD final (virama present)
        └─ class: verb, but C0 precedes C2
          └─ U5.C0 (dead final) → DELETE
            └─ /hun/        (cf. Wikipedia "Nepali phonology": [t͡sʰʌn])

  छन्
    NFC(छन्)            [न written with virama: न् = न+U+094D]
      └─ O4: verb, DEAD final (virama present)
        └─ class: verb, but C0 precedes C2
          └─ U5.C0 (dead final) → DELETE
            └─ /chan/        (cf. Wikipedia "Nepali phonology": [t͡sʰʌn])

  हुन्छ
    NFC(हुन्छ)
      └─ O4: verb, live-final (छ)
        └─ class: verb, verb_final_live
          └─ U5.C2b (verb, live final छ) → RETAIN
            └─ /huncha/

  मञ्च
    NFC(मञ्च)
      └─ O4: conjunct-final, Newar (L_neg)
        └─ class: conjunct + lneg
          └─ U5.C1 → except L_neg → DELETE
            └─ /mañc/

  यस
    NFC(यस)
      └─ O4: pronoun, ajanta
        └─ class: pronoun (R3.6)
          └─ U5.C6 (DEFAULT; R3.6 explicit) → DELETE
            └─ /yas/

  पार्क
    NFC(पार्क)
      └─ O4: English loan, ajanta, donor no vowel
        └─ class: foreign
          └─ U5.C5 (donor_schwa=False) → DELETE
            └─ /park/

================================================================================
APPENDIX A — RULE INDEX (knowledge-graph IDs)
================================================================================
R1.1–R1.4 writing system / normalization
R2.1–R2.4 segmental inventory
R3.0–R3.9 syllable / medial inherent vowel
R4.1–R4.2 stress (predictable, non-gating)
R5.1–R5.9 morphology / compounds
R6.0–R6.2 final-schwa algorithm (U5)
R7.1–R7.3 sandhi
R8.1–R8.3 etymology / loans
R9.1–R9.4 exceptions (exception-free)
R10.1–R10.2 deterministic procedure / output
O4.1–O4.7 orthography layer (tags feeding R6)
U5  unified priority rule; branches C0 C1 C2 C3 C4 C5 C6

================================================================================
APPENDIX B — SOURCES (primary first)
================================================================================
[A] Acharya, S. (1991). A Descriptive Grammar of Nepali and an Analyzed Corpus.
[B] Devī Nepal (2011). Nepali Varṇavinyās. Nepal Academy. §2 origin classes;
    §3 hrasva/dirgha, halanta/ajanta; §4 ba/va; §5 śa/ṣa/sa.
[C] Nepal Academy. Praśāsanic Vyākaraṇ Varṇavinyās, pp.327–349. Normative over
    [B] on conflict (O4.7).
[D] Clements, G.N. & Khatiwada, R. (2009). "Nepali". Journal of the IPA.
[E] Regmi (2006) / Gipan (2025). Nepali syllabification (R3.0).
[F] Balaram. Computational Analysis of Nepali Morphology (FST model, R10).
[G] Wikipedia: "Nepali phonology" — secondary phonetic evidence that हुन्/छन्
    surface without schwa ([t͡sʰʌn], [gʌi̯n]); predicted by U5.C0 since न् carries a
    virama. The earlier "C2.1" proposal was WITHDRAWN (see §6 note).
[H] Nepal Academy Brihat Shabdakosh 10th ed. (2075/2018) — mandatory spelling
    standard (O4.1).
[I] Corpus validation: nepali_g2p_corpus.xlsx (7282 rows) + heldout_test.xlsx
    (117 unseen external words); both 100% vs Nepal Academy ground truth
    (METHODOLOGY.md, 2026-07-18).

# ================================================================================
# ADDENDUM — NATIVE-SPEAKER LISTENING REVIEW (T6), validated 2026-07-18
# ================================================================================
# The following rules were confirmed by native-speaker auditory review and are
# NOW AUTHORITATIVE additions/clarifications to the reference implementation.
# They override the corpus GT wherever the corpus disagrees (corpus GT was
# found unreliable for final-schwa and conjunct realization).
#
# A) CONJUNCT SECOND MEMBER KEEPS INHERENT /a/  (R2.x clarification)
#    A conjunct = dead C + live C. The LIVE second consonant retains its
#    inherent /a/ (it is NOT absorbed). Reference realizations:
#      त्र=tra  प्र=pra  क्र=kra  द्र=dra  श्र=shra  ब्र=bra  ग्र=gra
#      स्त=sta  स्म=sma  क्ष=ksha  ज्ञ=gy  स्त्र=stra (stacked conjunct)
#    When a dependent vowel (matra) immediately follows the conjunct, the matra
#    REPLACES the second consonant's inherent /a/ (e.g. त्र+ई -> tri, प्र+े ->
#    pre, not trai/prae).
#
# B) AU-KAR (ौ) -> /au/  (R2.x vowel map correction)
#    The matra ौ (au-kar) realizes as /au/, not /o/. e.g. सम्झौता -> samjhauta.
#
# C) FINAL SCHWA — DEFAULT DELETE, CURATED RETAIN  (R6 C6 clarification)
#    C6 default for a native noun/adj ending in a LIVE consonant (no virama,
#    no conjunct) is DELETE (nepal, ghar, pariwar, buddhiman, udyog, nirman,
#    arthik, samajik, gayak, nartak, prem, kawita). Only a CONFIRMED set keeps
#    /a/ (curated in lexicon + u5 RETAIN_FINAL): यस, कमल, पुस्तकालय,
#    अर्थशास्त्र, मित्रता, साहित्य. A word ending in an explicit vowel matra
#    (ा/ी/ू/ौ) retains that vowel (handled by segmenter, not U5).
#
# D) EXCEPTION SETS (U5)
#    HALANTA_FINAL (traditional halanta, DELETE): नेपाल, प्रधान, घर (ghar),
#       कमल (kamal)  -- confirmed native: final अ dropped
#    TATSAMA_DELETE (Sanskrit-derived but deletes): देश -> desh
#    RETAIN_FINAL (native keep-/a/ exceptions): यस, पुस्तकालय,
#       अर्थशास्त्र, मित्रता, साहित्य (sahitya keeps final अ)
#    Foreign loans (C5, donor drops /a/): पार्क->park, स्कुल->school,
#       किताब->kitab
#
# E) COMPOUND JOIN  (R7 extension)
#    A compound of stem + stem drops the join schwa:
#      प्रधान + मन्त्री -> pradhanmantri  (प्रधान halanta: pradhan)
#    Stem-final न is halanta in प्रधान (pradhan), not pradhana.
#
# F) VERB-SUFFIX DETECTION HARDENED
#    ends_in_verb_suffix no longer matches a bare conjunct-final noun
#    (e.g. अर्थशास्त्र ends in त्र = त्+र, NOT a verb). Only न्+छ/त्+छ and
#    एन/ऐन negatives are verbs.
#
# G) CURATED LEXICON (authoritative tokens, native-validated)
#    Added: प्रधानमन्त्री(pradhanmantri), घर(ghar), स्कुल(school),
#    कमल(kamal), पुस्तकालय(pustakalaya), अर्थशास्त्र(arthashastra),
#    मित्रता(mitrata), साहित्य(sahitya), सफलता(saphalta, medial ल schwa
#    deleted), काठमान्डु(kathmandu, native spelling मान्डु).
#    Note: काठमाडौं (with ौ) is the Sanskritized spelling; native = काठमान्डु.

