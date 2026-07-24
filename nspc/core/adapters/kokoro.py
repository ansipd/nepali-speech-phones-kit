# -*- coding: utf-8 -*-
"""kokoro.py — canonical -> Kokoro TTS phoneme format & vocab.json.

Kokoro TTS (82M parameter lightweight style-based TTS model) uses a
phoneme string input and a `vocab.json` (token -> integer ID).

This adapter exports:
  1. `convert(tokens, format='ipa')`: converts canonical tokens to Kokoro phoneme input string.
  2. `build_vocab_json()`: builds a Kokoro-compatible `vocab.json` mapping pad, bos, eos,
     and all 40 canonical phonemes (or IPA symbols) to token IDs.
  3. `vocab_json_string()`: returns the JSON string formatted for Kokoro training/inference.
"""
import json
from .. import inventory as _inv


def convert(tokens, use_ipa=True):
    """Canonical tokens -> Kokoro-compatible phoneme text.
    If use_ipa is True, maps canonical tokens to IPA symbols; otherwise uses canonical tokens.
    """
    if use_ipa:
        return _inv.to_ipa(tokens)
    return " ".join(tokens)


def build_vocab_json(pad="_", bos="^", eos="$", use_ipa=True):
    """Generate a Kokoro-compatible vocab.json mapping from the canonical inventory.
    Maps special tokens and canonical phoneme symbols to integer IDs.
    """
    vocab = {pad: 0, bos: 1, eos: 2, " ": 3, ".": 4, ",": 5, "!": 6, "?": 7}
    if use_ipa:
        symbols = sorted(set(_inv.TO_IPA.values()))
    else:
        symbols = sorted(_inv.ALL_TOKENS)
    idx = len(vocab)
    for s in symbols:
        if s not in vocab:
            vocab[s] = idx
            idx += 1
    return vocab


def vocab_json_string(use_ipa=True):
    v = build_vocab_json(use_ipa=use_ipa)
    return json.dumps(v, ensure_ascii=False, indent=2)
