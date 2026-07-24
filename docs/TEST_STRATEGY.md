# TEST STRATEGY — proving "better pronunciation" WITHOUT a trained voice
# Companion to IMPLEMENTATION_ROADMAP.md. Answers: what can we test NOW
# (no GPU, no recorded dataset) vs what needs a model later.

KEY INSIGHT: the frontend emits LABELS (phoneme sequences). Labels are
testable directly — we do NOT need a synthesized voice to prove the
pronunciation logic is better than eSpeak `ne` or Ampixa real_nepali.

================================================================================
A. RUNNABLE NOW / SOON (no acoustic model)  — these answer "is it better?"
================================================================================

T1. SELF-CONSISTENCY REGRESSION  [STATUS: PASSING]
   - 7282 Academy-consistent + 117 genuinely held-out vs independent Academy
     ground truth. Currently 100%. Re-run after every core change.
   - File: tests/test_standard_regression.py (already green in repo).

T2. CROSS-IMPLEMENTATION AGREEMENT
   - reference_impl.py (spec) vs nspc/core/rules.py (port) must agree on every
     word in the regression set. Catches porting drift.
   - Add to tests/test_cross_impl.py after Phase 1.

T3. EXTERNAL DIFFERENTIAL BENCHMARK  [PRIORITY: highest empirical value]
   - For a fixed tricky-word set, render with:
       (a) eSpeak-ng `ne`  → e.g. च = ts, gemination lost, heuristic schwa
       (b) Ampixa real_nepali (if pip-installable) → its phonemes
       (c) OURS (nspc --format ipa)
   - Diff and TABULATE per word: where we differ and WHY (cite U5 branch).
   - Output: docs/benchmark_differential.md — a reproducible "better" proof.
   - Needs: espeak-ng installed (optional; degrade gracefully if absent).
   - Tricky set must include: conjunct-final (विकास,अन्त), tatsama (विकास,
     दुख,सुख,सरकार), verbs न्-final (हुन्,छन्,गर्नेछन्), gemination contexts,
     Nepanglish (अनलाइन,स्कुल), च/छ words (चिनियाँ,छाता).

T4. NATIVE-SPEAKER STRUCTURED AUDIT
   - Curated CSV (~200 rows): word | expected_IPA | U5_branch | notes.
   - Covers minimal pairs + known-hard classes (see T3 list + रत्न-compound,
     रस्व i/u medial, दीर्घ final). Each row = one assertion in
     tests/test_native_audit.py.
   - Metric: pass-rate %, tracked; must NOT regress across versions.
   - This is the human-grounded correctness gate (replaces "sounds ok").

T5. OOV STRESS TEST  [directly proves the Ampixa-fallback fix]
   - Feed 500 words absent from any lexicon. Assert:
       (a) every word gets a rule-derived pronunciation (no silent drop),
       (b) every emitted token ∈ INVENTORY.md (no invented symbols).
   - File: tests/test_oov.py.

T6. LISTENING-REVIEW SET + IPA SCRIPT
   - data/sample_sentences.txt: held-out + natural sentences.
   - Script: `nspc --file sentences.txt --format ipa > review.tsv`
     emits word | ipa | trace for human review.
   - Measures subjective naturalness (T7/T8 later) by human judgment NOW.

================================================================================
B. NEEDS A TRAINED MODEL (downstream; NOT blocking the kit)
================================================================================

T7. PERCEPTUAL MOS  — native listeners rate synthesized audio (needs voice).
T8. ASR-WER         — recognize synthesized speech, measure WER (needs voice+ASR).
   Both become possible once examples/piper_dataset or examples/matcha_dataset
   is used to train a voice. Out of kit scope; our frontend enables them.

================================================================================
C. METRICS WE TRACK (the "assurance" dashboard)
================================================================================
  - T1 regression agreement %           (target: 100, never regress)
  - T2 cross-impl agreement %           (target: 100)
  - T3 differential: # words where we≠eSpeak AND we are phonologically correct
  - T4 native-audit pass-rate %         (baseline set at v0.1, track upward)
  - T5 OOV coverage %                   (target: 100, zero silent drops)

================================================================================
D. DECISION
================================================================================
We RUN T1–T6 as part of the kit (no voice needed). T3 + T4 are the empirical
answer to "is our pronunciation better" — reproducible, citeable, and
regression-tracked. T7/T8 are deferred to when a voice is trained.
