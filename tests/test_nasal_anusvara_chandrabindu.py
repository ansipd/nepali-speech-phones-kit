# -*- coding: utf-8 -*-
"""
tests/test_nasal_anusvara_chandrabindu.py
=====================================================================
INVARIANT (locks in the ँ vs ं split — R3.4 of the Standard):

  Chandrabindu (ँ) -> PURE vowel nasalization (no consonant realized).
      e.g. सँग -> saga, सँगै -> sagai (the nasalized vowel only).

  Anusvara (ं) before a consonant -> HOMORGANIC nasal consonant by the
  place of the FOLLOWING consonant (Sanskrit anunasika sandhi, phonetically
  realized in Nepali), NOT vowel nasalization:
      velar    (कखगघङ)        -> ng   (संगीत -> sangit)
      palatal  (चछजझञ)        -> ny   (संज्ञ  -> sanj~nya)
      retroflex(टठडढण)         -> n
      dental   (तथदधन)         -> N    (संतति -> saNTaTi)
      labial   (पफबभम)         -> m    (संभव -> sambhav)
      semi/sibilant/h (यरलवशषसह) -> N (संस्कृति -> saNskriTi)

The OLD bug (treating ँ and ं identically by just nasalizing the preceding
vowel) is prevented: an anusvara before a stop must produce a nasal consonant
token, never a '~' on the vowel.

Exits non-zero on ANY violation.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, ".."))  # package root

from nspc.core import lexicon as _lex


def plain(tokens):
    """Tokens -> plain letters (strip '~' nasal marker for comparison)."""
    return "".join(t[:-1] if t.endswith("~") else t for t in tokens)


# (word, expected plain, note)
CASES = [
    # --- chandrabindu: vowel nasalization only, no nasal consonant ---
    ("सँग",   "saga",     "ँ -> vowel nasalization (सँ -> sa~)"),
    ("सँगै",  "sagai",    "ँ -> vowel nasalization (सँगै -> sa~gai = sagai)"),
    # --- anusvara before stops: homorganic nasal consonant ---
    ("संगीत", "sanggi:T", "ं before ग (velar) -> ng"),
    ("संभव",  "sambhaw",  "ं before भ (labial) -> m"),
    ("संस्कृति", "saNskrTi", "ं before स (sibilant) -> N"),
    ("संज्ञ",  "sanygy",   "ं before ज (palatal) -> ny"),
    ("हंस",   "haNs",     "ं before स (sibilant) -> N"),
    ("कंठ",   "kantha",   "ं before ठ (retroflex) -> n"),
    ("पंख",   "pangkha",  "ं before ख (velar) -> ng"),
]


def test_nasal_anusvara_chandrabindu():
    failures = []
    for word, expected, note in CASES:
        tokens, _, _, _, src = _lex.process(word)
        got = plain(tokens)
        if got != expected:
            failures.append((word, got, expected, note))
    assert not failures, "Nasal split failures: %s" % failures


if __name__ == "__main__":
    test_nasal_anusvara_chandrabindu()
    print("ALL NASAL SPLIT CHECKS PASS.")

