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

DEVANAGARI_RUN = re.compile(r"[\u0900-\u097f]+")
LATIN_RUN = re.compile(r"[A-Za-z]+")
DIGIT_RUN = re.compile(r"[0-9]+")
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


def is_loan_latin(surface):
    return surface.lower() in LOAN_LATIN
