# RULE DEPENDENCY GRAPH
# Nepali Computational Pronunciation Standard v1.0
# Textual representation of "what must run before what", and "what each rule
# gates". A rule may not be evaluated before all rules it DEPENDS ON have run.

LEGEND
  -->  "must run before" (data dependency)
  ==>  "gates / is consumed by"
  ORTHO external authority (Nepal Academy), not a computed rule

================================================================================
1. PIPELINE ORDER (execution sequence, R10.1)
================================================================================

  ORTHO(O4.1 authority)
     |
     v
  O4.2 origin tag --> O4.3 halanta/ajanta --> O4.4 raswa/dirgha
     |                  |                      |
     |                  v                      v
     |                R1.4 dead/live <-- R1.3 NFC
     |                  |                (ORTHO-dependent codepoint bounds)
     |                  v
     |                R6.0 tag tuple  <-- R8.1/R8.2/R8.3 etymology (consume O4.2)
     |                  |
     |                  v
  R1.1 akshara --> R1.2 charset --> R1.3 NFC --> R1.4 dead/live
                                              |
  R2.1 consonant map --+--> R3.9 /h/-del --+  |
  R2.2 vowel map -------+--> R7.1 asp-simp -+  |
  R2.3 glides ----------+                   |  |
  R2.4 visarga --------+                    |  v
                                            | R3.0 syllable envelope
                                            |   |
                                            |   v
                                            | R3.1/R3.2/R3.3/R3.5 medial /a/
                                            |   |        (R3.5b illicit-cluster)
                                            |   v
                                            | R5.9 compound (R4.1 CWSR + R3.5b)
                                            |   |
                                            v   v
                                          R6  U5  (final /a/; branches C0 C1 C2 C3 C4 C5 C6)
                                            |
                                            v
                                          R7.2 sandhi/gemination (on R6 output)
                                            |
                                            v
                                          R4.1 stress (quality only; non-gating)
                                            |
                                            v
                                          R10.2 output + trace (§12)

================================================================================
2. INDIVIDUAL RULE DEPENDENCIES
================================================================================

R1.1  akshara        : deps: none. gates: all downstream (defines the unit).
R1.2  charset        : deps: R1.1. gates: R1.3 (valid-codepoint check).
R1.3  NFC            : deps: R1.1, R1.2. gates: R1.4, R2.x, R3.x, R6.
R1.4  dead/live      : deps: R1.3. gates: R3.x, R6 (C0), R6.0.
R2.1  consonant map  : deps: R1.3. gates: R3.9, R5.2, R7.1, R7.2.
R2.2  vowel map      : deps: R1.1. gates: R3.3, R9.2.
R2.3  glides         : deps: R2.1. gates: output only.
R2.4  visarga        : deps: R1.1. gates: (silent) output only.
R3.0  syllable env   : deps: R1.1. gates: R3.5b, R5.9, R6 (C1 phonotactic basis).
R3.1  medial init    : deps: R1.4. gates: R6.2 dispatch (non-final).
R3.2  medial+dead    : deps: R1.4. gates: R6.2 dispatch.
R3.3  medial+nasal   : deps: R1.4, R2.2. gates: R6.2 dispatch.
R3.5  medial+conjunct: deps: R1.4. gates: R6.2 dispatch.
R3.5b illicit clust. : deps: R3.0. gates: R5.9.
R3.6  pronoun final  : deps: R6 (default C6). gates: overrides C3 misclass.
R3.9  /h/-del        : deps: R2.1. gates: segmental cleanup (pre-final).
R4.1  stress         : deps: R3.0 (weight). gates: R4.2, R5.9. NON-GATING for R6.
R4.2  reduction      : deps: R4.1. gates: vowel quality only. Independent of R6.
R5.1  local morph    : deps: R3.x, R6. gates: R7.2, O4.6.
R5.2  gemination     : deps: R2.1. gates: R7.2.
R5.3  suffix etym    : deps: R8, R6. gates: final /a/ tag.
R5.4  compound fin   : deps: R3.0, R3.5b. gates: R5.9.
R5.9  compound coup. : deps: R4.1, R3.5b, R5.4. gates: compound phonology.
R6.0  tag tuple      : deps: R1.3, R1.4, O4.2/O4.3. gates: R6 (U5).
R6    U5             : deps: R6.0, R1.4, R3.0, §11(O4). gates: output final /a/.
R6.1  ortho signature: deps: O4, R6. gates: debuggability only.
R6.2  medial dispatch : deps: R3.x, R6. gates: routing.
R7.1  asp-simp       : deps: R2.1. gates: segmental cleanup.
R7.2  sandhi         : deps: R5.2, R6 (output). gates: boundary output. NON-OVERRIDE of R6.
R7.3  sandhi≠R6      : deps: R6, R7.2. gates: interaction contract.
R8.1  etym tag       : deps: O4.2. gates: R6.0, R5.3, R8.2/8.3.
R8.2  L_neg class    : deps: R8.1. gates: R6 (C1 exception).
R8.3  naturalization : deps: R8.1. gates: R6 (C5 vs C6).
R9.1  no exceptions  : deps: R6. gates: coverage claim.
R9.2  R_LEN length   : deps: O4.4. gates: length only; NON-INTERACTING with R6.
R9.3  exhaustiveness : deps: R6, R8. gates: coverage claim.
R9.4  failure handle : deps: R6. gates: fallback (C5).
R10.1 procedure      : deps: ALL. gates: deterministic ordering.
R10.2 output         : deps: R10.1. gates: emits trace (§12).
O4.1  authority      : deps: external. gates: all O4.x.
O4.2  origin tag     : deps: O4.1. gates: R8.1.
O4.3  halanta/ajanta : deps: O4.1, R1.4. gates: R6.0.
O4.4  raswa/dirgha   : deps: O4.1. gates: R9.2.
O4.5  ba/va/śa       : deps: R2.1. gates: char maps (no schwa effect).
O4.6  padayoga       : deps: R5.1. gates: morpheme segmentation.
O4.7  conflict policy: deps: O4.1. gates: resolves [B] vs [C].

================================================================================
3. CRITICAL PATH (minimum rules to resolve the final /a/)
================================================================================

  R1.3 → R1.4 → O4.2/O4.3 → R8.1/R8.2 → R6.0 → R6 (U5)

If ONLY the final-schwa decision is needed (the core of this standard), the
minimal path is the above; all R2.x/R3.x-medial/R4/R5/R7 are orthogonal to the
final /a/ decision and may run in parallel or after, never before R6.0.

================================================================================
4. INDEPENDENCE / NON-INTERFERENCE CONTRACTS
================================================================================

  - R4 (stress) does NOT gate R6. A word's final /a/ is decided without
    consulting stress. (Contract R4.2.)
  - R9.2 (length) does NOT gate R6. Length and schwa are disjoint dimensions.
  - R7 (sandhi) does NOT override any R6 branch; it applies to R6's output at
    boundaries only. (Contract R7.3.)
  - O4 (orthography) is a TAG SOURCE for R6; it never computes pronunciation
    directly, so the specification and the Academy spelling standard cannot
    circularly validate each other. Validation uses an INDEPENDENT ground
    truth (METHODOLOGY.md), never O4 or the implementation.
  - reference_impl.py is ONE realization of R10; replacing it cannot change R6.
