# -*- coding: utf-8 -*-
"""matcha.py — canonical -> Matcha tokens.txt format.

Matcha-TTS uses a tokens.txt (one token per line, indexed). We emit the
canonical inventory as the token set and provide a text converter. A
`nepali_cleaners` stub shows where to plug the call (mirrors the mah92
Persian recipe: build a custom cleaner that calls nspc).

This adapter does NOT invent symbols; it uses the canonical set, so Matcha's
vocabulary == INVENTORY.md. No silent OOV fallback (the frontend already
guarantees coverage).
"""
from .. import inventory as _inv

_BOS = "<bos>"
_EOS = "<eos>"
_PAD = "<pad>"


def convert(tokens):
    """canonical tokens -> space-joined string for Matcha text input."""
    return " ".join(tokens)


def build_tokens_file(extra=None):
    """Generate the lines of a Matcha tokens.txt from the canonical inventory.
    Returns list[str] (one token per line). Include specials first."""
    specials = [_PAD, _BOS, _EOS]
    if extra:
        specials += list(extra)
    return specials + sorted(_inv.ALL_TOKENS)


def tokens_txt_string():
    return "\n".join(build_tokens_file())
