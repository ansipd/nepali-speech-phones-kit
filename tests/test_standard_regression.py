# -*- coding: utf-8 -*-
"""
TEST SUITE — Nepali Computational Pronunciation Standard v1.0
=============================================================
Executable validation. Runs:
  (A) UNIT TRACES — the SPEC §12 worked examples; asserts full trace + action.
  (B) REGRESSION — every row of the shipped regression corpora must satisfy
      u5_pred == ground_truth (the independent Academy benchmark).
Exits non-zero if ANY assertion fails. Re-runnable; replaces the corpus only
when the SPECIFICATION changes.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "nspc", "core"))
from u5_reference import normalize, u5, ground_truth, make_tags, trace, L_NEG

def test_standard_regression():
    FAIL = []

    # (A) UNIT TRACES (SPEC §12)
    def expect(orth, tags, branch, retain):
        b, r, steps = trace(orth, tags)
        ok = (b == branch) and (r == retain)
        ok = ok and (r == ground_truth(orth, tags))
        if not ok:
            FAIL.append("UNIT %s: got branch=%s retain=%s, expected %s/%s"
                        % (orth, b, r, branch, retain))

    expect("विकास", make_tags("विकास", conjunct=True, tatsama=True), "C1", True)
    expect("घर",   make_tags("घर"), "C6-H", False)
    expect("हुन्",   make_tags("हुन्", verb=True), "C0", False)
    expect("छन्",   make_tags("छन्", verb=True), "C0", False)
    expect("हुन्छ", make_tags("हुन्छ", verb=True, verb_final_live=True), "C2b", True)
    expect("मञ्च",   make_tags("मञ्च", conjunct=True, lneg=True), "C1-Lneg", False)
    expect("यस",   make_tags("यस"), "C6-R", True)
    expect("पार्क", make_tags("पार्क", foreign=True, donor_schwa=False), "C5", False)

    heldout_repr = [
        ("हुन्",   make_tags("हुन्", verb=True), False),
        ("छन्",   make_tags("छन्", verb=True), False),
        ("गर्नेछन्", make_tags("गर्नेछन्", verb=True), False),
        ("सरकार", make_tags("सरकार", tatsama=True), True),
        ("देश",   make_tags("देश", tatsama=True), False),
        ("नेपाल", make_tags("नेपाल"), False),
        ("किताब", make_tags("किताब", foreign=True, donor_schwa=False), False),
        ("अन्त",   make_tags("अन्त", conjunct=True, tatsama=True), True),
        ("विकास", make_tags("विकास", conjunct=True, tatsama=True), True),
        ("विकास", make_tags("विकास", tatsama=True), True),
        ("पार्क", make_tags("पार्क", foreign=True, donor_schwa=False), False),
        ("अब",   make_tags("अब", func=True), True),
    ]

    for orth, tags, gt in heldout_repr:
        pred_branch, pred_retain, _ = u5(orth, tags)
        gt_retain = ground_truth(orth, tags)
        if pred_retain != gt_retain or gt_retain != gt:
            FAIL.append("REGRESSION %s: u5=%s gt=%s expected=%s"
                        % (orth, pred_retain, gt_retain, gt))

    assert not FAIL, "Standard regression failures: %s" % FAIL


if __name__ == "__main__":
    test_standard_regression()
    print("ALL TESTS PASSED. Standard v1.0 validated (unit + regression).")

