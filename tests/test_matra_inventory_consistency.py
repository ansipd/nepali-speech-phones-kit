# -*- coding: utf-8 -*-
"""
SELF-CONSISTENCY TEST — matra map vs vowel inventory (T7).

Catches the class of bug where a Devanagari matra is mapped to a canonical
token whose phonetic length contradicts the inventory definition. This is the
bug Gemini's external audit found: matra ा (आ, dirgha/long) was mapped to 'a'
(short schwa), making every आ sound like a short schwa in synthesis.

The plain-letter display renders both 'a' and 'a:' as "a", so this bug is
INVISIBLE to letter-level review and only surfaces when tokens are mapped to
IPA/sound. This test checks the mapping at the token level against the
linguistic ground truth in docs/INVENTORY.md.

Rule (from INVENTORY.md):
  - inherent vowel (no matra)  -> 'a'   (short schwa /ə/)
  - SHORT matras  ि �ु े ो      -> short tokens  i u e o
  - LONG  matras  ा ी ू ौ      -> long tokens   a: i: u: au
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from nspc.core import rules as R

# (matra, expected_token, length_label)
EXPECT = [
    ("\u093e", "a:",  "LONG"),   # ा  आ dirgha
    ("\u093f", "i",   "SHORT"),  # ि  इ hrasva
    ("\u0940", "i:",  "LONG"),   # ी  ई dirgha
    ("\u0941", "u",   "SHORT"),  # ु  उ hrasva
    ("\u0942", "u:",  "LONG"),   # ू  ऊ dirgha
    ("\u0947", "e",   "SHORT"),  # े  ए (e)
    ("\u0948", "e",   "SHORT"),  # ै  ऐ -> e
    ("\u094b", "o",   "SHORT"),  # ो  ओ (o)
    ("\u094c", "au",  "LONG"),   # ौ  औ au-kar
]

LONG_TOKENS = {"a:", "i:", "u:", "au"}  # au-kar (औ) is dirgha-class/long


def main():
    fails = []
    for matra, exp, label in EXPECT:
        got = R.MATRA_TO_VOWEL.get(matra)
        ok = (got == exp)
        if not ok:
            fails.append("matra %s -> got %r, expected %r (%s)" %
                         (matra, got, exp, label))
        else:
            # cross-check length consistency
            is_long = got in LONG_TOKENS
            if label == "LONG" and not is_long:
                fails.append("matra %s -> %r is not a LONG token (invariant violated)"
                             % (matra, got))
            if label == "SHORT" and is_long:
                fails.append("matra %s -> %r is not a SHORT token (invariant violated)"
                             % (matra, got))
        print("matra %s -> %-4s  [%s]  %s" %
              (matra, got, label, "OK" if ok else "FAIL"))
    # inherent vowel sanity: a token must exist and be short
    if "a" in LONG_TOKENS:
        fails.append("inherent 'a' token must be SHORT, not long")
    print()
    if fails:
        print("FAILED:")
        for f in fails:
            print("  - " + f)
        sys.exit(1)
    print("ALL MATRA-INVENTORY CONSISTENCY CHECKS PASS.")


if __name__ == "__main__":
    main()
