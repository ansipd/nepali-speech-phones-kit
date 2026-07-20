# -*- coding: utf-8 -*-
"""
nspc/core/normalize_text.py
=====================================================================
Sentence-level normalization BEFORE word G2P (R1.1, R1.2):
  - strip punctuation that is not part of words
  - split into word tokens (Devanagari runs vs Latin/number runs)
  - normalize Nepali digits -> words? No: map digits to a neutral token;
    full number-to-word is engine/locale specific, left to the trainer.
  - keep code-switch (Latin) words as separate tokens for the foreign path.

This module does NOT do G2P; it only tokenizes + flags token types so the
frontend can route each token correctly (native / foreign / number).
"""
import re

from . import numbers as _numbers
from . import mixed_script as _mixed

DEVANAGARI_RUN = re.compile(r"[\u0900-\u097f]+")
LATIN_RUN = re.compile(r"[A-Za-z]+")
DIGIT_RUN = re.compile(r"[0-9]+")
# Digit run incl. Devanagari digits and an optional decimal point.
NUM_RUN = re.compile(r"[०-९0-9]+(?:\.[०-९0-9]+)?")
PUNCT = set("।,;.!?\"'()[]{}:/-")

# Common Latin-in-Nepali loanwords (transliteration path, not letter-fallback)
LOAN_LATIN = {
    "online": "अनलाइन",
    "school": "स्कुल",
    "bus": "बस",
    "college": "कलेज",
    "phone": "फोन",
    "computer": "कम्प्युटर",
}


def tokenize(text):
    """Return list of dicts: {surface, kind} where kind in
    {devanagari, latin, digit, punct}."""
    tokens = []
    # split on whitespace first, then classify each chunk
    for chunk in text.split():
        # strip surrounding punctuation
        stripped = chunk.strip("".join(PUNCT))
        if not stripped:
            continue
        if DEVANAGARI_RUN.fullmatch(stripped):
            tokens.append({"surface": stripped, "kind": "devanagari"})
        elif LATIN_RUN.fullmatch(stripped):
            tokens.append({"surface": stripped, "kind": "latin"})
        elif DIGIT_RUN.fullmatch(stripped):
            tokens.append({"surface": stripped, "kind": "digit"})
        else:
            # mixed; emit as-is, kind 'other'
            tokens.append({"surface": stripped, "kind": "other"})
    return tokens


def expand_numbers(text, formal=False):
    """Return `text` with every digit run replaced by its Nepali word form
    (via nspc.core.numbers). Non-digit content is preserved verbatim.
    This is the text-normalization step that turns numerals into spelled-out
    Devanagari words BEFORE word-level G2P."""
    return _numbers.normalize_numbers_in_text(text, formal=formal)


def normalize_text_pipeline(text, formal=False):
    """Canonical sentence-normalization entry point. Runs, in order:
      1. mixed_script  — Roman -> Devanagari (two-tier: whitelist + dynamic),
                         so the rest of the pipeline only sees Devanagari/digits.
      2. expand_numbers — digit runs -> Devanagari word tokens.
    Returns the normalized Devanagari string ready for word-level G2P.
    """
    text = _mixed.normalize_mixed_script(text)
    return expand_numbers(text, formal=formal)


def tokenize_with_numbers(text, formal=False):
    """Tokenize `text` and expand any digit token into Devanagari WORD
    tokens (so the downstream G2P sees real words, not bare digits).

    Returns a list of {surface, kind} dicts. Digit runs become one or more
    'devanagari' word tokens; date-context grouping (1100-1999) is applied
    when a run is immediately followed by a date keyword (साल/वर्ष/सम्म/को).
    """
    tokens = []
    # Pre-convert any Roman tokens to Devanagari so downstream G2P sees only
    # Devanagari (and digits). Roman->Devanagari is the first pipeline step.
    text = _mixed.normalize_mixed_script(text)
    for chunk in text.split():
        stripped = chunk.strip("".join(PUNCT))
        # Preserve a leading minus sign that immediately precedes a digit run
        # (e.g. "-15") so the number module can convert it to माइनस. The
        # generic punctuation strip above would otherwise drop the sign.
        if chunk and chunk[0] in "-−–—" and stripped and stripped[0] in "०१२३४५६७८९0123456789":
            stripped = chunk[0] + stripped
        if not stripped:
            continue
        # expand digit runs inside the chunk, then classify each resulting word
        expanded = _numbers.normalize_numbers_in_text(stripped, formal=formal)
        for word in expanded.split():
            if DEVANAGARI_RUN.fullmatch(word):
                tokens.append({"surface": word, "kind": "devanagari"})
            elif LATIN_RUN.fullmatch(word):
                tokens.append({"surface": word, "kind": "latin"})
            else:
                tokens.append({"surface": word, "kind": "other"})
    return tokens


def is_loan_latin(surface):
    return surface.lower() in LOAN_LATIN
