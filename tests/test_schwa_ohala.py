# -*- coding: utf-8 -*-
"""
tests/test_schwa_ohala.py
=====================================================================
Regression tests for the Ohala-style internal schwa-deletion rule
(liquids/glides as medial codas): C1-LIQUID-C3-V -> the liquid drops
its inherent /a/ (coda), the vowel belongs to C3.

Native-confirmed targets (stem + suffix compounds):
    सरकार -> sarka:r   (स keeps /a/, र coda drops, का=long /a:/)
    तरबार -> Tarba:r   (त keeps, र coda drops)
    सलवार -> salwa:r   (स keeps, ल coda drops)
    तलवार -> Talwa:r   (त keeps, ल coda drops)

PROTECTED cases (liquid KEEPS /a/ -- it is a peak or final, not a coda):
    कमल   -> kamal     (ल word-final)
    करण   -> karan     (ण word-final -> र keeps)
    शकिरा -> shakira:  (र immediately followed by its own matra ा -> peak)
    बन्द   -> baNDa     (न dead conjunct; no liquid coda)

Run:  $env:PYTHONPATH="."; py tests/test_schwa_ohala.py
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nspc.core import lexicon as L


_CASES = [
    # (word, expected_tokens, note)
    ("सरकार", ["s", "a", "r", "k", "a:", "r"], "स keeps, र coda drops, का long"),
    ("तरबार", ["T", "a", "r", "b", "a:", "r"], "त keeps, र coda drops"),
    ("सलवार", ["s", "a", "l", "w", "a:", "r"], "स keeps, ल coda drops"),
    ("तलवार", ["T", "a", "l", "w", "a:", "r"], "त keeps, ल coda drops"),
    # protected
    ("कमल",   ["k", "a", "m", "a", "l"], "ल word-final keeps"),
    ("करण",   ["k", "a", "r", "a", "n"], "ण word-final -> र keeps; final ण drops अ (C6)"),
    ("शकिरा", ["sh", "a", "k", "i", "r", "a:"], "र peak (own matra) keeps"),
    ("बन्द",   ["b", "a", "N", "D", "a"], "न dead conjunct, no liquid coda"),
]


def _render(tokens):
    return "".join(tokens)


def main():
    failures = 0
    print("=== (Ohala) INTERNAL SCHWA / LIQUID-CODA REGRESSION ===")
    for word, exp, note in _CASES:
        got, _, _, _, src = L.process(word)
        ok = got == exp
        if not ok:
            failures += 1
        print("  %-10s exp=%-14s got=%-14s [%s] %s" % (
            word, _render(exp), _render(got), "OK" if ok else "FAIL", note))
    if failures:
        print("FAILED (%d)" % failures)
        sys.exit(1)
    print("ALL OHALA SCHWA CHECKS PASS (%d)." % len(_CASES))
    sys.exit(0)


if __name__ == "__main__":
    main()
