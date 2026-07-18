# -*- coding: utf-8 -*-
"""
examples/build_dataset.py
=====================================================================
Copy-paste starter that turns a Devanagari text/lexicon into the metadata
format a TTS trainer expects, using OUR frontend (not eSpeak/Ampixa).

Two output modes:
  --trainer piper   -> emits lines: <wav_path>\t<phoneme_string>
  --trainer matcha  -> emits lines: <wav_path>\t<phoneme_string>

The phoneme_string is the CANONICAL token sequence from nspc (space-joined),
which adapters translate to the trainer's exact symbol set. This file shows
how to REPLACE eSpeak/Ampixa in an existing pipeline with nspc.

Usage:
  py examples/build_dataset.py --trainer piper --text "नमस्ते नेपाल" --out meta.tsv
"""
import sys
import os
import argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nspc.core import lexicon as _lex
from nspc.core import normalize_text as _nt
from nspc.core.adapters import piper as _piper
from nspc.core.adapters import matcha as _matcha


def build(text, trainer):
    lx = _lex.default()
    out = []
    for tok in _nt.tokenize(text):
        if tok["kind"] == "devanagari":
            toks, tags, br, ret, src = lx.process(tok["surface"])
            phon = _piper.convert(toks) if trainer == "piper" else _matcha.convert(toks)
        elif tok["kind"] == "latin":
            phon = tok["surface"].lower()  # foreign fallback
        else:
            continue
        out.append((tok["surface"], phon))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trainer", choices=["piper", "matcha"], required=True)
    ap.add_argument("--text", default="नमस्ते नेपाल")
    ap.add_argument("--out")
    args = ap.parse_args()

    rows = build(args.text, args.trainer)
    lines = ["\t".join(r) for r in rows]
    content = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        print("wrote", args.out)
    else:
        print(content)


if __name__ == "__main__":
    main()
