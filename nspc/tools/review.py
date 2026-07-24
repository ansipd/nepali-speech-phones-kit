# -*- coding: utf-8 -*-
"""
data/sample_sentences.txt reader + review emitter (T6).

Emits, for every word, three columns:
  DEV          Devanagari surface (for Notepad)
  READ         simple-letter reading (no IPA symbols)
  IPA          canonical IPA (for experts)

The terminal often renders Devanagari badly (scattered/boxed glyphs) on
PowerShell / some Linux terminals. The reliable fix is to write a UTF-8 file
and open it in Notepad (or any editor with Devanagari shaping). Use --out.

Run:
  py -m nspc.tools.review                 # prints to terminal
  py -m nspc.tools.review --out t6.txt    # writes UTF-8 file for Notepad
"""
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..", "..")
_SENTENCES = os.path.join(_ROOT, "data", "sample_sentences.txt")

# Simple-letter reading map (NOT IPA): every token -> a normal Latin letter so a
# non-coder can sound the word out. अ -> 'a' (short neutral vowel).
_SIMPLE = {
    "a": "a", "a:": "a", "i": "i", "i:": "i", "u": "u", "u:": "u",
    "e": "e", "o": "o", "a~": "an", "i~": "in", "u~": "un", "e~": "en",
    "o~": "on", "r~": "ri",
    "k": "k", "kh": "kh", "g": "g", "gh": "gh", "ng": "ng",
    "c": "ch", "ch": "ch", "j": "j", "jh": "jh", "ny": "ny",
    "t": "t", "th": "th", "d": "d", "dh": "dh", "n": "n",
    "T": "t", "Th": "th", "D": "d", "Dh": "dh", "N": "n",
    "p": "p", "ph": "ph", "b": "b", "bh": "bh", "m": "m",
    "y": "y", "r": "r", "l": "l", "w": "b", "s": "s",
    "sh": "sh", "S": "sh", "h": "h", "ks": "ksh", "jn": "gy", "tr": "tr",
}


def _simp(toks):
    return "".join(_SIMPLE.get(t, t) for t in toks)


def _build(args):
    from nspc.core import lexicon as _lex
    from nspc.core import inventory as _inv
    from nspc.core import normalize_text as _nt
    lx = _lex.default()
    out = []
    with open(args.sentences, encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    out.append("=== NSPC-Kit listening-review set (T6) ===")
    out.append("Total sentences: %d" % len(lines))
    out.append("")
    out.append("Columns:  DEV (Devanagari) | READ (simple letters) | IPA")
    out.append("")
    for li, sent in enumerate(lines, 1):
        out.append("--- sentence %d ---" % li)
        out.append("DEV: " + sent)
        words = [t["surface"] for t in _nt.tokenize(sent)
                 if t["kind"] == "devanagari"]
        for w in words:
            toks, tags, br, ret, src = lx.process(w)
            out.append("  %-12s | %-14s | %s  [%s]" %
                       (w, _simp(toks), _inv.to_ipa(toks), src))
        out.append("")
    return "\n".join(out)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="NSPC-Kit T6 listening-review set")
    ap.add_argument("--sentences", default=_SENTENCES,
                    help="path to a UTF-8 file of one sentence per line")
    ap.add_argument("--out", default=None,
                    help="write UTF-8 review to this file (open in Notepad)")
    args = ap.parse_args()
    text = _build(args)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("Wrote review to: " + os.path.abspath(args.out))
    else:
        print(text)


if __name__ == "__main__":
    main()
