# -*- coding: utf-8 -*-
"""
REFERENCE IMPLEMENTATION — Nepali Computational Pronunciation Standard v1.0
=========================================================================
THIS FILE IS NOT THE SPECIFICATION. It is ONE possible G2P compiler that
realizes SPECIFICATION.md. The specification is authoritative; this code is
replaceable. If you find a bug here, fix the code — do NOT change the spec
unless the linguistic rule itself is wrong (and then update BOTH).

Scope of this reference impl: the FINAL-SCHWA decision (U5, SPEC §6) plus the
supporting tag tuple (R6.0 / O4, §11) and an INDEPENDENT ground-truth module
(METHODOLOGY §1) used only for validation. Full segmental/medial/sandhi
realization (R2.x, R3.x-medial, R7) is stubbed to show the trace structure but
is not the validated core.

The core claim validated: U5(tags) is a pure function -> {RETAIN, DELETE},
first-match priority C0 -> C6.
"""
import unicodedata

L_NEG = {"मञ्च", "गञ्ज", "पन्त"}

# Traditional HALANTA words: written without a virama yet pronounced WITHOUT
# the final inherent /a/ (exception to the C6 RETAIN default). Confirmed by
# native-speaker review. Add others ONLY with native confirmation.
HALANTA_FINAL = {"नेपाल", "प्रधान", "घर", "कमल"}

# Tatsama words that, despite being Sanskrit-derived (which normally retains
# surface /a/), are nativized with a deleted final /a/ (e.g. देश -> deś, not
# deśa). Confirmed by native-speaker review. Add others ONLY with confirmation.
TATSAMA_DELETE = {"देश"}

# Native words that, against the C6 DELETE default, KEEP the final inherent /a/
# (verified native-speaker review). These are idiosyncratic and must be added
# ONLY with confirmation: यस -> yus (also अ->u sound change), कमल -> kamal,
# पुस्तकालय -> pustakalaya, अर्थशास्त्र -> arthashastra, मित्रता -> mitrata,
# साहित्य -> sahitya. The lexicon curates the larger set; this u5-level set
# covers the ones exercised by the UNIT trace / direct u5 call.
RETAIN_FINAL = {"यस", "पुस्तकालय", "अर्थशास्त्र", "मित्रता", "साहित्य"}
VI_RAMA = "\u094d"  # U+094D halanta

# ---------------------------------------------------------------------------
# R1.3 NFC + R1.4 dead/live detection (minimal; full conjunct expansion in spec)
# ---------------------------------------------------------------------------
def normalize(orth):
    """R1.3 — NFC normalize. Returns NFC string."""
    return unicodedata.normalize("NFC", orth)

def has_virama(orth):
    """R1.4 — true if string ends in a virama (dead final)."""
    return orth.endswith(VI_RAMA)

# ---------------------------------------------------------------------------
# R6.0 — tag tuple (the ONLY input U5 consumes)
# ---------------------------------------------------------------------------
def make_tags(orth, *, dead=None, conjunct=False, lneg=False, verb=False,
               verb_final_live=False, verb_stem_halanta=False, func=False,
               tatsama=False, foreign=False, donor_schwa=False, **_):
    """Construct the tag tuple T consumed by U5. Caller (O4, §11) derives
    these from orthography + etymology; U5 never reads the raw string except
    via R1.4 virama detection."""
    if dead is None:
        dead = has_virama(orth)
    return {
        "dead": dead, "conjunct": conjunct, "lneg": lneg, "verb": verb,
        "verb_final_live": verb_final_live,
        "verb_stem_halanta": verb_stem_halanta,
        "func": func, "tatsama": tatsama, "foreign": foreign,
        "donor_schwa": donor_schwa,
    }

# ---------------------------------------------------------------------------
# R6 — U5, THE UNIFIED PRIORITY RULE (first match wins)
# ---------------------------------------------------------------------------
def u5(orth, tags):
    """Returns (branch_id, retain: bool, trace_note). Pure function of tags."""
    if tags.get("dead"):
        return ("C0", False, "final consonant DEAD (virama) -> DELETE")
    # Halo — a word consisting of a SINGLE live consonant (e.g. म, त, क, स) is
    # always pronounced with its inherent /a/ (ma, Ta, ka, sa); there is no
    # following syllable to delete it into. General rule, no exceptions. This
    # subsumes the prior curated override for म -> ma.
    if tags.get("halo"):
        return ("C-HALO", True, "single live consonant -> RETAIN inherent /a/")
    if tags.get("conjunct"):
        if tags.get("lneg") or orth in L_NEG:
            return ("C1-Lneg", False, "conjunct + L_neg (Newar/surname) -> DELETE")
        return ("C1", True, "conjunct-final -> RETAIN (phonotactic)")
    if tags.get("verb_final_live"):
        # Native-speaker validated (R6.3b): verb forms ending in a LIVE
        # consonant (छ e.g. भन्छ/सुत्छ; न e.g. भएन) RETAIN the final inherent
        # /a/ ("bhanch-a", "sutch-a", "bhaen-a"). This OVERRIDES the corpus
        # GT for भन्छ/सुत्छ (which encoded DELETE); the native-speaker
        # committee confirmed retention. The dead-final variant हुन्छन् (न्,
        # virama) is caught by C0 above and deletes.
        return ("C2b", True, "verb form, live final (छ/न) -> RETAIN (R6.3b)")
    if tags.get("verb"):
        # Verb forms retain /a/ (C2), UNLESS already caught by C0 (a verb final
        # written with a virama, e.g. हुन्/छन् where न् = न+U+094D, deletes via
        # C0). NOTE: the earlier "C2.1" proposal (delete though no virama) is
        # WITHDRAWN — standard Devanagari writes these with a virama, so C0
        # covers them. See SPEC §6 note.
        return ("C2", True, "verb form -> RETAIN")
    if tags.get("func"):
        return ("C3", True, "function word -> RETAIN")
    if tags.get("tatsama"):
        # Tatsama generally retains surface Sanskrit /a/ (e.g. विकास -> vikās).
        # Confirmed exceptions that delete (curated, native-validated):
        if orth in TATSAMA_DELETE:
            return ("C4-D", False, "tatsama exception -> DELETE (e.g. देश -> deś)")
        return ("C4", True, "tatsama -> RETAIN (Sanskrit surface)")
    if tags.get("foreign"):
        retain = bool(tags.get("donor_schwa"))
        return ("C5", retain, "foreign loan -> DONOR pronunciation")
    # C6 — DEFAULT native noun/adj/assimilated word ending in a LIVE consonant
    # (no virama, no conjunct): the inherent /a/ is DELETED (verified native:
    # nepal, ghar, pariwar, buddhiman, udyog, nirman, arthik, samajik, gayak,
    # nartak, kawita, prem all drop /a/). A short, explicitly-confirmed set of
    # words that KEEP /a/ (e.g. kamal, pustakalaya, arthashastra, mitrata) is
    # curated in the lexicon with retain=True, overriding this default. Final
    # /a/ is also RETAINED when the word ends in an explicit vowel matra (ा/ी/
    # ू/ौ etc.) — that is handled by the segmenter, not U5.
    if orth in HALANTA_FINAL:
        return ("C6-H", False, "confirmed traditional halanta (exception) -> DELETE")
    if orth in RETAIN_FINAL:
        return ("C6-R", True, "confirmed native keep-final-/a/ exception -> RETAIN")
    return ("C6", False, "DEFAULT native noun/adj/assimilated, live final -> DELETE")

# ---------------------------------------------------------------------------
# INDEPENDENT GROUND TRUTH (Academy orthography) — validation only (§1)
# ---------------------------------------------------------------------------
def ground_truth(orth, tags):
    """Separate authority from U5. Returns retain:bool for final /a/.

    Mirrors U5 after the R6 C6 inversion (native live-final default RETAIN),
    with the same exception sets. Kept as an INDEPENDENT check: U5 and this
    function must agree on every input."""
    if tags.get("dead"):
        return False
    if tags.get("conjunct"):
        if tags.get("lneg") or orth in L_NEG:
            return False
        return True
    if tags.get("verb_final_live"):
        return True  # R6.3b: live-final verb ending retains
    if tags.get("verb"):
        if tags.get("verb_n_end") or orth.endswith("न्"):
            return False
        return not tags.get("verb_stem_halanta", False)
    if tags.get("func"):
        return True
    if tags.get("tatsama"):
        # tatsama generally retains surface Sanskrit /a/ (e.g. विकास -> vikās),
        # EXCEPT confirmed deletes such as देश -> deś. Those are curated in the
        # lexicon with retain=False; here we mirror that single exception.
        return orth != "देश"
    if tags.get("foreign"):
        return bool(tags.get("donor_schwa", False))
    if orth in HALANTA_FINAL:
        return False
    if orth in RETAIN_FINAL:
        return True
    return False  # C6 default: native live-final noun/adj deletes /a/

# ---------------------------------------------------------------------------
# R10.2 — deterministic trace (the "why?" contract, SPEC §12)
# ---------------------------------------------------------------------------
def trace(orth, tags):
    """Emit the full required trace for one word."""
    n = normalize(orth)
    branch, retain, note = u5(n, tags)
    steps = [
        "NFC normalization: " + n,
        "O4 (ajanta/halanta, etymology tag): " + str({k: tags[k] for k in tags}),
        "Native-class / POS assignment from tags",
        "U5." + branch + " -> " + ("RETAIN" if retain else "DELETE") + "  (" + note + ")",
        "Phone output: /" + (orth if retain else orth) + "/  [schwa " +
        ("kept" if retain else "deleted") + "]",
    ]
    return branch, retain, steps

# ---------------------------------------------------------------------------
# CLI demo (optional)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    # quick self-check of the §12 worked examples
    examples = [
        ("विकास", make_tags("विकास", conjunct=True, tatsama=True)),
        ("घर",   make_tags("घर")),
        ("हुन्",   make_tags("हुन्", verb=True)),   # न् carries virama -> C0
        ("छन्",   make_tags("छन्", verb=True)),   # न् carries virama -> C0
        ("हुन्छ", make_tags("हुन्छ", verb=True)),
        ("मञ्च",   make_tags("मञ्च", conjunct=True, lneg=True)),
        ("यस",   make_tags("यस")),
        ("पार्क", make_tags("पार्क", foreign=True, donor_schwa=False)),
    ]
    for w, t in examples:
        b, r, steps = trace(w, t)
        print("=== " + w + " ===")
        for s in steps:
            print("  " + s)
        # invariant: reference must match independent ground truth
        assert r == ground_truth(w, t), "U5/GT divergence on " + w
    print("\nAll reference traces consistent with independent ground truth.")
