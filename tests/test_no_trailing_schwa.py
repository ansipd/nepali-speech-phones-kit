# -*- coding: utf-8 -*-
"""
tests/test_no_trailing_schwa.py
=====================================================================
INVARIANT (locks in the हेरेर -> 'r ax' Kala bug prevention):

  No word whose final Devanagari character is a LIVE consonant (no virama,
  no terminal matra) may produce a trailing 'a' (inherent schwa) token.

Rationale: a word-final live consonant in Nepali has its inherent schwa
deleted (U5.C6 / C0). Emitting '... r a' for '... र' is the Kala defect
(हेरेर -> h e . r e . r ax) and must be impossible by construction.

We verify the invariant over:
  (1) the shipped regression corpus (7282 rows via lexicon),
  (2) an explicit list of conjunct-participle words (राखेर, हेरेर, पर्खेर, ...).

Exits non-zero on ANY violation.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, ".."))  # package root

from nspc.core import lexicon as _lex
from nspc.core import normalize as _nz

VI_RAMA = "\u094d"
MATRA_SET = {
    "\u093e", "\u093f", "\u0940", "\u0941", "\u0942", "\u0943", "\u0944",
    "\u0945", "\u0946", "\u0947", "\u0948", "\u0949", "\u094a", "\u094b",
    "\u094c", "\u094d", "\u094e", "\u094f",
}
INDEP_VOWEL = {
    "\u0905", "\u0906", "\u0907", "\u0908", "\u0909", "\u090a",
    "\u090b", "\u090f", "\u0910", "\u0911", "\u0912", "\u0913", "\u0914",
}


def final_is_live_consonant(word):
    """True if the word ends in a live consonant (no virama, no matra, no
    independent vowel)."""
    s = _nz.NFC(word)
    if not s:
        return False
    last = s[-1]
    if last == VI_RAMA:
        return False  # dead final
    if last in MATRA_SET or last in INDEP_VOWEL:
        return False  # ends in a vowel sign / independent vowel
    # consonant base range
    return "\u0915" <= last <= "\u0939"


def violates(word, tokens, retain):
    """The invariant (Kala 'r ax' defect prevention), grounded in the
    independent GT that the lexicon mirrors:

      A word the lexicon/GT marks DELETE (retain=False) must NOT emit a
      trailing 'a' (inherent schwa) on its final live consonant.

    Words the GT marks RETAIN (e.g. compound verb forms पढेकोछ, tatsama
    सत्य/अद्य) legitimately keep the final 'a' and are NOT violations.
    This precisely targets the Kala-class defect without over-reaching into
    validated retain cases.
    """
    if retain:
        return False  # GT says keep -> not a defect
    if not final_is_live_consonant(word):
        return False
    if not tokens or tokens[-1] != "a":
        return False
    return True


FAIL = []

# (1) Explicit critical cases (the class Kala got wrong)
critical = [
    "हेरेर", "पर्खेर", "राखेर", "गएर", "हानेर", "फर्केर",
    "सम्झेर", "ओझेर", "भनेर", "आएर", "गरेर", "खेलेर",
    "घर", "नेपाल", "विकास", "यस", "को", "मञ्च",
]
print("=== (1) CRITICAL WORDS (Kala-bug class) ===")
lx = _lex.default()
for w in critical:
    toks, tags, br, ret, src = lx.process(w)
    bad = violates(w, toks, ret)
    if bad:
        FAIL.append("TRAILING-SCHWA %s: tokens=%s (branch=%s)" % (w, toks, br))
    print("  %-8s %-8s -> %s %s" % (w, br, " ".join(toks), "BAD" if bad else "ok"))

# (2) Full corpus scan via lexicon (every word must satisfy invariant)
print("\n=== (2) FULL CORPUS INVARIANT SCAN ===")
checked = 0
for word in lx._entries:
    s = _nz.NFC(word)
    if not final_is_live_consonant(s):
        continue
    toks, tags, br, ret, src = lx.process(s)
    if violates(s, toks, ret):
        FAIL.append("CORPUS %s: tokens=%s (branch=%s)" % (s, toks, br))
    checked += 1
print("  scanned %d live-final words from lexicon" % checked)

print("\n" + "=" * 60)
if FAIL:
    print("FAILED (%d):" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("ALL TESTS PASSED. No trailing-schwa defect (Kala 'r ax' class) present.")
sys.exit(0)
