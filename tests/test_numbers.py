# -*- coding: utf-8 -*-
"""
tests/test_numbers.py
=========================================================================
Verify the Nepali number verbalization module (nspc.core.numbers) and its
integration into the sentence tokenizer (normalize_text.tokenize_with_numbers).

Native-validated expectations:
  - १ / 1      -> एक
  - 2026        -> दुई हजार छब्बिस   (year == count; no "बिस सय" form)
  - 1990        -> एक हजार नौ सय नब्बे  (standard math, no context)
  - 1990साल     -> उन्नाइस सय नब्बे साल (date context -> grouped by hundreds)
  - 12.5        -> बाह्र प्वाइन्ट पाँच  (modern point word)
  - 12.55       -> बाह्र प्वाइन्ट पाँच पाँच (fractional digits read individually)
  - 12.5 formal -> बाह्र दशमलव पाँच  (formal separator)
  - Devanagari digits १२.५ behave identically to ASCII 12.5
"""
import sys, os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nspc.core import numbers as N
from nspc.core import normalize_text as T


def check(name, got, expected):
    ok = got == expected
    print("  %-22s -> %s   %s" % (name, " ".join(got), "OK" if ok else "FAIL (exp %s)" % " ".join(expected)))
    return ok


def main():
    fails = 0
    print("=== (Numbers) cardinal / year / decimal ===")

    fails += 0 if check("१", N.verbalize_int("१"), ["एक"]) else 1
    fails += 0 if check("1", N.verbalize_int("1"), ["एक"]) else 1
    fails += 0 if check("2026", N.verbalize_int("2026"), ["दुई", "हजार", "छब्बिस"]) else 1
    fails += 0 if check("1990 (no ctx)", N.verbalize_int("1990"),
                        ["एक", "हजार", "नौ", "सय", "नब्बे"]) else 1
    fails += 0 if check("1990 (date)", N.verbalize_int("1990", is_date=True),
                        ["उन्नाइस", "सय", "नब्बे"]) else 1
    fails += 0 if check("12.5", N.verbalize_decimal("12.5"),
                        ["बाह्र", "प्वाइन्ट", "पाँच"]) else 1
    fails += 0 if check("12.55", N.verbalize_decimal("12.55"),
                        ["बाह्र", "प्वाइन्ट", "पाँच", "पाँच"]) else 1
    fails += 0 if check("12.5 formal", N.verbalize_decimal("12.5", formal=True),
                        ["बाह्र", "दशमलव", "पाँच"]) else 1
    fails += 0 if check("१२.५ (deva)", N.verbalize_decimal("१२.५"),
                        ["बाह्र", "प्वाइन्ट", "पाँच"]) else 1

    # text-level date-context grouping
    txt = N.normalize_numbers_in_text("1990साल")
    ok = txt == "उन्नाइस सय नब्बे साल"
    print("  %-22s -> %s   %s" % ("normalize 1990साल", txt, "OK" if ok else "FAIL"))
    fails += 0 if ok else 1

    # tokenizer integration: digit -> devanagari word tokens
    toks = T.tokenize_with_numbers("2026 साल 12.5")
    kinds = [(t["surface"], t["kind"]) for t in toks]
    expected_kinds = [("दुई", "devanagari"), ("हजार", "devanagari"),
                      ("छब्बिस", "devanagari"), ("साल", "devanagari"),
                      ("बाह्र", "devanagari"), ("प्वाइन्ट", "devanagari"),
                      ("पाँच", "devanagari")]
    ok = kinds == expected_kinds
    print("  %-22s -> %s   %s" % ("tokenize_with_numbers", kinds, "OK" if ok else "FAIL"))
    fails += 0 if ok else 1

    print("\n" + "=" * 60)
    if fails:
        print("FAILED (%d)" % fails)
        sys.exit(1)
    print("ALL NUMBER CHECKS PASS.")
    sys.exit(0)


if __name__ == "__main__":
    main()
