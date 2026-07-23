# -*- coding: utf-8 -*-
"""
nspc/core/normalize.py
=====================================================================
Orthographic normalization + automatic tag inference for Nepali
Devanagari (R1.1-R1.4, O4). This module turns RAW unicode text into
the tag tuple (R6.0) that U5 consumes. It is the piece the reference
impl left to "the caller": here we make it deterministic and automatic
so the frontend needs no hand-supplied tags.

Design: pure, no pretrained model, no external resources. Everything
is derivable from Unicode + the Standard v1.0 facts.

Functions:
  NFC(text)                 -> NFC-normalized string (R1.3)
  is_dead(s)                -> ends in virama U+094D (R1.4)
  split_chars(s)            -> list of unicode chars
  detect_conjuncts(s)       -> set of conjunct clusters (dead C + live C)
  auto_tag(word, **etym)    -> tag dict for U5 (R6.0)
  analyze(word)             -> dict of structural facts (debug/trace)
"""
import unicodedata
import re

VI_RAMA = "\u094d"  # U+094D halanta (dead consonant marker)

# Devanagari consonant base range (without inherent vowel / matra).
# We treat any char followed by a virama as "dead", then a following
# live consonant = conjunct. A simpler, robust heuristic for Nepali:
#   - a virama followed by another consonant => conjunct context
#   - trailing virama => dead final
# We do NOT need the full consonant set; we detect by virama presence.

# Matras (dependent vowels) used to detect ajanta vs halanta word shape.
_MATRA_SET = {
    "\u093e", "\u093f", "\u0940", "\u0941", "\u0942", "\u0943",
    "\u0944", "\u0945", "\u0946", "\u0947", "\u0948", "\u0949",
    "\u094a", "\u094b", "\u094c", "\u094d", "\u094e", "\u094f",
    "\u0900", "\u0901", "\u0902", "\u0903",  # chandrabindu, anusvara, visarga
}

# L_neg class (Newar-origin / surname conjunct-final; C1-Lneg -> DELETE).
L_NEG = {"मञ्च", "गञ्ज", "पन्त"}


def NFC(text):
    """R1.3 — canonical composition."""
    return unicodedata.normalize("NFC", text)


# Spelling variants that are phonetically identical (native-confirmed): the same
# word is written two ways. We map the less-common spelling onto the canonical
# one so the rule engine needs only ONE entry. Confirmed by native review:
#   मंच (anusvara ं) == मञ्च (conjunct ञ) -> both "manch".
_SPELLING_VARIANTS = {
    "\u092e\u0902\u091a": "\u092e\u091e\u094d\u091a",  # मंच -> मञ्च
}


def canonicalize(text):
    """R1.3b — NFC + collapse native-confirmed spelling variants to one form.
    Applied at the entry point of both segment() and lexicon.process so the
    engine treats मंच and मञ्च identically."""
    s = NFC(text)
    if s in _SPELLING_VARIANTS:
        return _SPELLING_VARIANTS[s]
    return s


def is_dead(s):
    """R1.4 — true if the string ends in a virama (dead final consonant)."""
    return s.endswith(VI_RAMA)


# Devanagari consonant base range (KA..HA, U+0915..U+0939). Excludes matras,
# virama, chandrabindu/anusvara, and independent vowels (अ..औ, U+0905..U+0914).
_CONSONANT_BASE = ("\u0915", "\u0939")


def is_consonant_base(c):
    """True if char c is a Devanagari consonant base (no inherent-vowel mark)."""
    return "\u0915" <= c <= "\u0939"


def is_halo(s):
    """True if the word is a single live consonant with NO matra / vowel mark /
    virama (e.g. म, त, क, स). Such a word is always pronounced with its
    inherent /a/ (ma, Ta, ka, sa) — there is no following syllable to absorb it.
    A consonant WITH a matra (मा, कि) or virama (क्) is NOT a halo."""
    cps = list(NFC(s))
    if len(cps) != 1:
        return False
    return is_consonant_base(cps[0])


def split_chars(s):
    """Return list of unicode characters (Devanagari is not one-codepoint-per-
    grapheme; virama+consonant form conjuncts but we keep raw cps)."""
    return list(s)


def _has_virama_before_letter(s):
    """True if any virama is followed by a non-virama char (i.e. a conjunct or
    dead-and-then-something). Used to detect conjunct clusters."""
    cps = list(s)
    for i, c in enumerate(cps):
        if c == VI_RAMA and i + 1 < len(cps) and cps[i + 1] != VI_RAMA:
            return True
    return False


def detect_conjuncts(s):
    """Return a list of conjunct clusters found as (deadC, liveC) boundaries.
    A conjunct = a dead consonant (C + virama) immediately followed by a live
    consonant. We report each 'X\u094dY' as a conjunct, and also whether the
    final consonant is dead."""
    conjuncts = []
    cps = list(s)
    i = 0
    while i < len(cps):
        if cps[i] == VI_RAMA and i + 1 < len(cps):
            # preceding live char (we may have already consumed the base)
            if i >= 1:
                prev = cps[i - 1]
                nxt = cps[i + 1]
                # prev is the dead consonant base, nxt is the following live consonant
                conjuncts.append((prev, nxt))
                i += 2
                continue
        i += 1
    return conjuncts


def _ends_with_conjunct_final(s):
    """True if the word ends in a conjunct whose SECOND member is the terminal
    (i.e. ...C1 virama C2  and C2 is the last char -> conjunct-final)."""
    cps = list(s)
    n = len(cps)
    if n >= 3 and cps[n - 2] == VI_RAMA:
        # last-char preceded by virama => the last char is a live consonant
        # attached to a dead one -> conjunct-final shape
        return True
    return False


def _word_ends_in_dead(s):
    """True if the final shape is a single dead consonant (...C + virama)."""
    return s.endswith(VI_RAMA)


# Verb-final suffix shapes: the cluster at word-end is a MORPHOLOGICAL boundary
# (stem + verb suffix), NOT a true C1 conjunct that retains its vowel.
# e.g. भन्छ = भन् + छ (न्+छ), सुत्छ = सुत् + छ, हुन्छ = हुन् + छ,
#      भन्एन = भन् + ए + न (ए+न verb-negative), सुतएन = सुत् + ए + न.
# In all these the terminal consonant (छ/न/र) is word-final and its inherent
# schwa is DELETED (C0), exactly as the independent Academy GT dictates.
# Treating न्+छ / ए+न as a plain C1 conjunct would wrongly RETAIN the final
# schwa (the Kala 'r ax' class of defect). We detect this and suppress C1.
_VERB_FINAL_LAST = {"\u091b", "\u0930", "\u0928"}  # छ, र, न
_EE_MATRA = "\u0947"   # े (ए matra)
_EE_INDEP = "\u090f"   # ए (independent vowel)
_EE_AI_MATRA = "\u0948" # ै (ऐ matra)
_EE_AI_INDEP = "\u0910"  # ऐ (independent vowel)


def ends_in_verb_suffix(s):
    """True if the word ends in a verb-final suffix whose terminal consonant's
    inherent schwa is deleted (C0/C6), not retained (C1).

    IMPORTANT: a bare conjunct-final noun such as अर्थशास्त्र (ends in त्र =
    त्+र) or ग्रन्थ (ends in न्थ) must NOT be treated as a verb. The verb
    pattern is specific: the verb ENDING छ (after a virama: न्+छ / त्+छ), or a
    negative एन/ऐन (ए/े/ै + न|र). A generic 'virama + {र,न}' match would
    wrongly fire on conjunct-final nouns — that is excluded here."""
    cps = list(s)
    n = len(cps)
    if n < 2:
        return False
    # ends in virama (न्) -> verb negative/final (also caught by C0 dead-final)
    if cps[-1] == VI_RAMA:
        return True
    # verb ending छ after a virama: न्+छ / त्+छ (भन्छ, सुत्छ, हुन्छ)
    if cps[-2] == VI_RAMA and cps[-1] == "\u091b":
        return True
    # verb negative एन/ऐन: ए/े/ै + (न|र)  e.g. भएन, सुतएन
    if cps[-2] in (_EE_MATRA, _EE_INDEP, _EE_AI_MATRA, _EE_AI_INDEP) and cps[-1] in _VERB_FINAL_LAST:
        return True
    # infinitive उन (independent vowel उ + न) for words longer than साउन (4).
    # साउन is a month name (not a verb) and ends in the same characters.
    if n >= 5 and cps[-2] == "\u0909" and cps[-1] == "\u0928":
        return True
    # negative इन (independent vowel इ + न) e.g. होइन (hoina), पाइन
    if n >= 3 and cps[-2] == "\u0907" and cps[-1] == "\u0928":
        return True
    return False


def verb_final_live(word):
    """True if the word is a verb form whose ABSOLUTE FINAL consonant is LIVE
    (not a virama). Per native-speaker validation these RETAIN the final
    inherent /a/:
        भन्छ  (न्+छ, ends in live छ) -> 'bhanch-a'  (retain)
        सुत्छ  (त्+छ, ends in live छ) -> 'sutch-a'   (retain)
        भएन  (ए+न, ends in live न)  -> 'bhaen-a'    (retain)
    Contrast with हुन्छन् which ends in न् (virama, DEAD) -> deletes (C0).
    NOTE: this OVERRIDES the corpus GT for भन्छ/सुत्छ (which encoded DELETE);
    native-speaker committee confirmed live-final verb endings retain. See
    SPECIFICATION.md R6.3b."""
    cps = list(NFC(word))
    n = len(cps)
    if n < 2:
        return False
    if cps[-1] == VI_RAMA:
        return False  # dead final (न्) -> not live-final-retain
    # live छ after a virama (न्+छ / त्+छ)
    if cps[-2] == VI_RAMA and cps[-1] == "\u091b":
        return True
    # live न/र after ए/ऐ (matra or independent vowel)  e.g. भएन, छैन
    if cps[-2] in (_EE_MATRA, _EE_INDEP, _EE_AI_MATRA, _EE_AI_INDEP) and cps[-1] in _VERB_FINAL_LAST:
        return True
    # infinitive उन (independent vowel उ + live न) for words longer than साउन (4)
    if n >= 5 and cps[-2] == "\u0909" and cps[-1] == "\u0928":
        return True
    # negative इन (independent vowel इ + live न) e.g. होइन (hoina)
    if n >= 3 and cps[-2] == "\u0907" and cps[-1] == "\u0928":
        return True
    return False


def analyze(word):
    """Return a dict of structural facts for a single word (already NFC).
    Used by trace + tests."""
    s = NFC(word)
    return {
        "nfc": s,
        "codepoints": [hex(ord(c)) for c in s],
        "dead_final": _word_ends_in_dead(s),
        "conjunct_final": _ends_with_conjunct_final(s),
        "conjunct_clusters": detect_conjuncts(s),
        "has_virama": VI_RAMA in s,
        "in_lneg": s in L_NEG,
    }


def auto_tag(word, **etym):
    """R6.0 — build the tag tuple for U5 automatically from orthography,
    merging any explicitly supplied etymological overrides (**etym).

    The purely orthographic facts (dead, conjunct, lneg) are inferred here.
    Etymological facts (verb/func/tatsama/foreign) must be supplied by the
    caller (lexicon or classifier) — they cannot be reliably read from the
    script alone. Defaults: everything off except what orthography implies.

    Returns dict suitable for u5(orth, tags).
    """
    s = NFC(word)
    facts = analyze(s)
    # A final conjunct whose terminal is a verb suffix is NOT a C1 conjunct.
    # Dead-final verb endings (न्) delete (C0); LIVE-final verb endings (छ/न)
    # RETAIN (R6.3b, native-speaker validated). Suppress conjunct so U5 does
    # not wrongly retain/delete via C1.
    is_verb_final = ends_in_verb_suffix(s)
    is_verb_final_live = verb_final_live(s)
    tags = {
        # dead = virama at the very end of the word (single dead final C),
        # OR a dead-final verb suffix (न्).
        "dead": facts["dead_final"] or (is_verb_final and not is_verb_final_live),
        # halo = a single live consonant with no matra/virama (म, त, क, स).
        # Always retains inherent /a/. High priority in U5 (after C0 dead).
        "halo": is_halo(s),
        # conjunct = word ends in a conjunct cluster (...C virama C[final]),
        # EXCEPT when that cluster is a verb-suffix (handled separately).
        "conjunct": facts["conjunct_final"] and not is_verb_final,
        "lneg": facts["in_lneg"],
        # Etymology — supplied by lexicon/classifier, never guessed:
        "verb": etym.get("verb", False) or is_verb_final,
        # NEW: live-final verb ending (भन्छ/सुत्छ/भएन) -> RETAIN (R6.3b).
        "verb_final_live": is_verb_final_live,
        "verb_stem_halanta": etym.get("verb_stem_halanta", False),
        "func": etym.get("func", False),
        "tatsama": etym.get("tatsama", False),
        "foreign": etym.get("foreign", False),
        "donor_schwa": etym.get("donor_schwa", False),
    }
    # If a conjunct-final word is also in L_neg, tag it; the conjunct flag
    # already set, lneg already set. U5 handles priority.
    # A dead-final (virama at very end) is reported as 'dead' not 'conjunct'.
    return tags


def auto_tag_full(word, **etym):
    """Like auto_tag but also infer conjunct even when not final-position
    (e.g. medial conjuncts). U5 only keys on FINAL schwa, but the trace
    reports all conjuncts for transparency."""
    tags = auto_tag(word, **etym)
    s = NFC(word)
    facts = analyze(s)
    tags["_medial_conjuncts"] = facts["conjunct_clusters"]
    return tags
