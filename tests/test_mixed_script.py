# -*- coding: utf-8 -*-
"""
tests/test_mixed_script.py
=========================================================================
Verify the mixed-script (Roman -> Devanagari) preprocessing step
(nspc.core.mixed_script) and its integration as the first step of the
normalization pipeline (nspc.core.normalize_text.normalize_text_pipeline).

Native-validated expectations:
  - "facebook नचलाइ station जाने हो र?"
      -> "फेसबुक नचलाइ स्टेसन जाने हो र?"   (whitelist + pure Devanagari untouched)
  - Pure Devanagari passes through untouched.
  - Digit runs are NOT touched by mixed_script (left for the number module).
  - After the full pipeline, Roman tokens become 'devanagari' kind tokens.

NOTE: this test does not require the optional indicxlit dependency; it verifies
the whitelist path and the offline rule-based fallback.
"""
import sys, os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nspc.core import mixed_script as M
from nspc.core import normalize_text as T


def check(name, got, expected):
    ok = got == expected
    print("  %-26s -> %s   %s" % (name, got, "OK" if ok else "FAIL (exp %s)" % expected))
    return ok


def main():
    fails = 0
    print("=== (Mixed-script) Roman -> Devanagari ===")

    fails += 0 if check("facebook+station",
                        M.normalize_mixed_script("facebook नचलाइ station जाने हो र?"),
                        "फेसबुक नचलाइ स्टेसन जाने हो र?") else 1

    # whitelist single token
    fails += 0 if check("hello", M.normalize_mixed_script("hello"),
                        "हेलो") else 1

    # pure Devanagari untouched
    fails += 0 if check("pure devanagari",
                        M.normalize_mixed_script("नेपाल सुन्दर छ"),
                        "नेपाल सुन्दर छ") else 1

    # digits untouched by mixed_script (number module handles them later)
    fails += 0 if check("digits untouched",
                        M.normalize_mixed_script("म 2026 सालमा 50% गए"),
                        "म 2026 सालमा 50% गए") else 1

    # full pipeline integrates mixed-script + numbers
    pipe = T.normalize_text_pipeline("facebook नचलाइ station जाने हो र?")
    ok = pipe == "फेसबुक नचलाइ स्टेसन जाने हो र?"
    print("  %-26s -> %s   %s" % ("pipeline", pipe, "OK" if ok else "FAIL"))
    fails += 0 if ok else 1

    # tokenization: Roman tokens become devanagari kind after pipeline
    toks = T.tokenize_with_numbers("facebook नचलाइ station जाने हो र?")
    kinds = [(t["surface"], t["kind"]) for t in toks]
    ok = kinds == [("फेसबुक", "devanagari"), ("नचलाइ", "devanagari"),
                   ("स्टेसन", "devanagari"), ("जाने", "devanagari"),
                   ("हो", "devanagari"), ("र", "devanagari")]
    print("  %-26s -> %s   %s" % ("tokenize", kinds, "OK" if ok else "FAIL"))
    fails += 0 if ok else 1

    print("\n" + "=" * 60)
    if fails:
        print("FAILED (%d)" % fails)
        sys.exit(1)
    print("ALL MIXED-SCRIPT CHECKS PASS.")
    sys.exit(0)


if __name__ == "__main__":
    main()
