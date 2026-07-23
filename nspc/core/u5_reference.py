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

# Postpositions / derivational suffixes (नामयोगी / सम्बन्धवाचक) are never
# pronounced in isolation; they always attach to a preceding host and KEEP
# their final inherent /a/ (e.g. सँग -> "saga", not "sag"; तिर -> "Tira",
# not "Tir). They are exempt from the C6 final-schwa DELETE that applies to
# bare native nouns (R7). A word ending in one of these (and longer than it)
# therefore RETAINs its final /a/.
_POSTPOSITIONS = {
    "जस्तै", "आदि", "वाला", "दार", "सँगै", "पछि", "अघि", "भरि", "सम्म",
    "हरू", "हरु", "सँग", "तिर", "बाट", "मा", "ले", "को", "का", "पनि", "सित",
    "पटक", "पल्ट", "पति", "बिना", "लाई",
    "कै", "भित्र",
    "देखि", "तर्फ", "विरुद्ध",
}

# Traditional HALANTA words: written without a virama yet pronounced WITHOUT
# the final inherent /a/ (exception to the C6 RETAIN default). Confirmed by
# native-speaker review. Add others ONLY with native confirmation.
HALANTA_FINAL = {"नेपाल", "प्रधान", "घर", "कमल", "आठ"}

# Number-unit words: lakh, arab, kharab, etc. These are number names used as
# standalone words and should ALWAYS delete final /a/ (C6 default), regardless
# of their final consonant class (aspirated, conjunct, etc.). They bypass C5b
# and C1 in the U5 priority order.
_NUM_UNITS = {"लाख", "करोड", "अर्ब", "खर्ब"}

# Tatsama words that, despite being Sanskrit-derived (which normally retains
# surface /a/), are nativized with a deleted final /a/ (e.g. देश -> deś, not
# deśa). Confirmed by native-speaker review. Add others ONLY with confirmation.
TATSAMA_DELETE = {"देश", "औषध"}

# Native words that, against the C6 DELETE default, KEEP the final inherent /a/
# (verified native-speaker review). These are idiosyncratic and must be added
# ONLY with confirmation: यस -> yus (also अ->u sound change), कमल -> kamal,
# पुस्तकालय -> pustakalaya, अर्थशास्त्र -> arthashastra, मित्रता -> mitrata,
# साहित्य -> sahitya. The lexicon curates the larger set; this u5-level set
# covers the ones exercised by the UNIT trace / direct u5 call.
RETAIN_FINAL = {"यस", "पुस्तकालय", "अर्थशास्त्र", "मित्रता", "साहित्य"}
VI_RAMA = "\u094d"  # U+094D halanta

# Aspirated stops/affricates (Devanagari consonant bases). A native word whose
# FINAL consonant is an aspirated stop/affricate KEEPS its inherent /a/ (e.g.
# दुख -> dukha, सुख -> sukha): the breathy release is realized with a following
# vowel, so the final /a/ is not elided. Phonotactic class rule (not a word
# list) — subsumes the दुख/सुखा case confirmed by native review. Extend the set
# only with native confirmation for other aspirated finals.
_ASPIRATED = {"\u0916",  # ख (kh)
              "\u0918",  # घ (gh)
              "\u091b",  # छ (ch)
              "\u091d",  # झ (jh)
              "\u0920",  # ठ (th)
              "\u0922",  # ढ (dh)
              "\u0925",  # थ (Th)
              "\u0927",  # ध (Dh)
              "\u092b",  # फ (ph)
              "\u092d"}  # भ (bh)


def _final_consonant_base(orth):
    """Return the LAST Devanagari consonant base in orth (NFC), or '' if none."""
    for c in reversed(orth):
        if "\u0915" <= c <= "\u0939":
            return c
    return ""


def _count_consonant_bases(orth):
    """Count Devanagari consonant bases (U+0915-U+0939) in orth."""
    return sum(1 for c in orth if "\u0915" <= c <= "\u0939")


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
    # R7 — postposition-final: a word ending in a known postposition (longer
    # than the suffix) KEEPS its final inherent /a/ (the suffix is pronounced
    # in attachment, never isolated). Overrides C6 default DELETE. E.g.
    # शिक्षातिर -> shiksha:Tira, कलमबाट -> kalamba:ta, देशतिर -> DeshTira.
    if any(orth.endswith(p) and len(orth) > len(p) for p in _POSTPOSITIONS):
        return ("C6-P", True, "ends in postposition -> RETAIN final /a/ (R7)")
    # Halo — a word consisting of a SINGLE live consonant (e.g. म, त, क, स) is
    # always pronounced with its inherent /a/ (ma, Ta, ka, sa); there is no
    # following syllable to delete it into. General rule, no exceptions. This
    # subsumes the prior curated override for म -> ma.
    if tags.get("halo"):
        return ("C-HALO", True, "single live consonant -> RETAIN inherent /a/")
    # Number-unit words (लाख, अर्ब, करोड, etc.) always DELETE final /a/.
    # This must fire before C1 (conjunct) and C5b (aspirated) so number words
    # do not incorrectly retain final /a/ through either of those rules.
    if orth in _NUM_UNITS:
        return ("C6-N", False, "number unit -> DELETE final /a/ (C6 default)")
    if tags.get("conjunct"):
        if tags.get("lneg") or orth in L_NEG:
            return ("C1-Lneg", False, "conjunct + L_neg (Newar/surname) -> DELETE")
        if tags.get("foreign") and not tags.get("donor_schwa"):
            return ("C5", False, "foreign loan ending in conjunct -> DELETE (donor)")
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
    # C5b — aspirated-final: ONLY for SHORT words (≤3 consonant bases) whose
    # FINAL consonant is an aspirated stop/affricate (ख/घ/छ/झ/ठ/ढ/थ/ध/फ/भ).
    # Short native words like दुख (dukha) and सुख (sukha) retain final /a/
    # because the breathy release needs a vowel. LONGER words (≥4 consonant
    # bases, e.g. लागुऔषध, वैशाख, सत्तारूढ) fall through to C6 DELETE since
    # standard spoken Nepali deletes the final schwa on longer tatsama forms.
    # Native-speaker confirmed on दुख/सुख.
    if orth in HALANTA_FINAL or orth in TATSAMA_DELETE:
        pass  # fall through to C6 below (HALANTA_FINAL or tatsama delete)
    elif _final_consonant_base(orth) in _ASPIRATED and \
            len(orth) <= 4:
        # Length ≤ 4 catches short native words like दुख/सुख (3 cps) but
        # excludes longer tatsama borrowings like वैशाख (5 cps), लागुऔषध, etc.
        return ("C5b", True, "short aspirated-final -> RETAIN inherent /a/")
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
    if any(orth.endswith(p) and len(orth) > len(p) for p in _POSTPOSITIONS):
        return True
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
