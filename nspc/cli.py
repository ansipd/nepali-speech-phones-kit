# -*- coding: utf-8 -*-
"""
nspc/cli.py — command line frontend for the NSPC-Kit.

Examples
--------
  nspc --text "नमस्ते" --format ipa
  nspc --text "विकास" --format json
  nspc --file sentences.txt --format piper
  nspc --text "स्कुल" --format matcha
  nspc --tokens-file            # print the canonical inventory tokens
  nspc --piper-map              # print Piper phoneme_id_map
  nspc --matcha-tokens          # print Matcha tokens.txt

The CLI is a thin consumer of the core + adapters. It NEVER contains
linguistic rules.
"""
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")

from .core import lexicon as _lex
from .core import trace as _trace
from .core import normalize_text as _nt
from .core.adapters import ipa as _ipa
from .core.adapters import json as _json
from .core.adapters import piper as _piper
from .core.adapters import matcha as _matcha
from .core.adapters import kokoro as _kokoro


def _process_text(text, fmt):
    lx = _lex.default()
    results = []
    for tok in _nt.tokenize(text):
        surface = tok["surface"]
        kind = tok["kind"]
        if kind == "devanagari":
            toks, tags, br, ret, src = lx.process(surface)
            tr = _trace.trace_word(surface)
            results.append({
                "text": surface, "tokens": toks, "branch": br,
                "source": src, "trace": tr["steps"],
            })
        elif kind == "latin":
            # foreign/loan path: transliterate if known else letter-fallback
            if _nt.is_loan_latin(surface):
                dev = _nt.LOAN_LATIN[surface.lower()]
                toks, tags, br, ret, src = lx.process(dev)
                results.append({"text": surface, "tokens": toks,
                                "branch": br, "source": src,
                                "trace": ["loan-latin -> " + dev]})
            else:
                # mark as OOV foreign; trainer decides donor pronunciation
                results.append({"text": surface, "tokens": list(surface.lower()),
                                "branch": "C5", "source": "rule",
                                "trace": ["unknown-latin (foreign)"]})
        else:
            results.append({"text": surface, "tokens": [surface],
                            "branch": None, "source": "other",
                            "trace": ["non-word token skipped"]})
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(prog="nspc", description="Nepali Speech Phones Kit")
    ap.add_argument("--text", help="Devanagari (or mixed) text")
    ap.add_argument("--file", help="path to a text file")
    ap.add_argument("--format", choices=["ipa", "json", "piper", "matcha", "kokoro"],
                    default="ipa")
    ap.add_argument("--tokens-file", action="store_true",
                    help="print canonical inventory tokens and exit")
    ap.add_argument("--piper-map", action="store_true",
                    help="print Piper phoneme_id_map and exit")
    ap.add_argument("--matcha-tokens", action="store_true",
                    help="print Matcha tokens.txt and exit")
    ap.add_argument("--kokoro-vocab", action="store_true",
                    help="print Kokoro vocab.json and exit")
    args = ap.parse_args(argv)

    if args.tokens_file:
        from .core import inventory as _inv
        print(" ".join(sorted(_inv.ALL_TOKENS)))
        return 0
    if args.piper_map:
        import json as _j
        print(_j.dumps(_piper.build_phoneme_id_map(), ensure_ascii=False))
        return 0
    if args.matcha_tokens:
        print(_matcha.tokens_txt_string())
        return 0
    if args.kokoro_vocab:
        print(_kokoro.vocab_json_string())
        return 0

    if not args.text and not args.file:
        ap.error("provide --text or --file (or a --* meta flag)")

    text = args.text or ""
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

    results = _process_text(text, args.format)

    if args.format == "ipa":
        for r in results:
            print(r["text"], "->", _ipa.convert(r["tokens"]))
    elif args.format == "json":
        print(_json.dumps(results))
    elif args.format == "piper":
        for r in results:
            print(r["text"], "->", _piper.convert(r["tokens"]))
    elif args.format == "matcha":
        for r in results:
            print(r["text"], "->", _matcha.convert(r["tokens"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
