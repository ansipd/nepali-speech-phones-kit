# -*- coding: utf-8 -*-
"""ipa.py — canonical -> IPA (for humans / publication / audit)."""
from .. import inventory as _inv


def convert(tokens):
    """tokens (list[str]) -> IPA string with spaces between phones."""
    return _inv.to_ipa(tokens)


def convert_word(tokens):
    return "/" + _inv.to_ipa(tokens) + "/"
