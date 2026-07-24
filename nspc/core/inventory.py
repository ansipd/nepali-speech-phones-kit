# -*- coding: utf-8 -*-
"""
nspc/core/inventory.py
=====================================================================
Canonical phone inventory — the single source of truth for all adapters
(INVENTORY.md, Phase 0). Every emitted token MUST be a member of this set.
Adapters translate canonical tokens -> engine-specific symbols; they never
invent new tokens.

Policy notes (Standard v1.0):
  - च/छ = palatal /tʃ/ /tʃʰ/ (D1). Canonical tokens: 'c' and 'ch'.
  - Gemination is rendered as a DOUBLE token (e.g. 'g gʱ'), NOT a length mark.
  - These are abstract canonical tokens, not IPA. The ipa adapter maps them.
"""
from typing import Set, Dict

# ---------------------------------------------------------------------------
# Vowels (canonical tokens)
# ---------------------------------------------------------------------------
VOWELS = {
    "a",    # inherent /a/  (realized [ə]~[ʌ])
    "a:",   # दीर्घ /aː/   (का, आ)
    "i",    # इ
    "i:",   # ई
    "u",    # उ
    "u:",   # ऊ
    "e",    # ए
    "o",    # ओ
    "a~",   # अनुनासिक a (चिनियाँ ाँ)
    "i~",   # इँ
    "u~",   # उँ
    "e~",   # एँ
    "o~",   # ओँ
    "ri",   # ऋ (modern Nepali)
    "ai",   # ऐ (diphthong; from ै matra and independent ऐ)
    "au",   # औ (au-kar, dirgha diphthong; from ौ matra)
    "a:~",  # आँ (nasalized long a; from ाँ, e.g. माँ, हाँ)
    "ai~",  # ऐँ (nasalized ai; from ैँ, e.g. कहैँ)
    "au~",  # औँ (nasalized au; from ौँ, e.g. गौं)
}

# ---------------------------------------------------------------------------
# Consonants (canonical tokens). 'c'/'ch' = PALATAL tʃ/tʃʰ per D1.
# ---------------------------------------------------------------------------
CONSONANTS = {
    "k", "kh", "g", "gh", "ng",   # क ख ग घ ङ
    "c", "ch", "j", "jh", "ny",   # च(=tʃ) छ(=tʃʰ) ज झ ञ
    "t", "th", "d", "dh", "n",    # ट ठ ड ढ ण
    "T", "Th", "D", "Dh", "N",    # त थ द ध न  (capital = dental)
    "p", "ph", "b", "bh", "m",    # प फ ब भ म
    "y", "r", "l", "v",           # य र ल व (v = labiodental /ʋ/)
    "s",                          # स (alveolar s)
    "sh",                         # श (palatal ʃ)
    "S",                          # ष (retroflex ʂ)
    "h",                          # ह
    "ks",                         # क्ष
    "jn",                         # ज्ञ
    "tr",                         # त्र
}

# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------
ALL_TOKENS: Set[str] = set(VOWELS) | set(CONSONANTS)
VALID = ALL_TOKENS

# ---------------------------------------------------------------------------
# Canonical -> IPA (for humans / publication). D1 confirmed.
# ---------------------------------------------------------------------------
TO_IPA: Dict[str, str] = {
    "a": "ə", "a:": "aː", "i": "i", "i:": "iː", "u": "u", "u:": "uː",
    "e": "e", "o": "o", "a~": "ã", "i~": "ĩ", "u~": "ũ", "e~": "ẽ",
    "o~": "õ", "ri": "ri", "au": "au", "a:~": "ãː", "au~": "ãu",
    "k": "k", "kh": "kʰ", "g": "ɡ", "gh": "ɡʱ", "ng": "ŋ",
    "c": "tʃ", "ch": "tʃʰ", "j": "dʒ", "jh": "dʒʱ", "ny": "ɲ",
    "t": "ʈ", "th": "ʈʰ", "d": "ɖ", "dh": "ɖʱ", "n": "ɳ",
    "T": "t", "Th": "tʰ", "D": "d", "Dh": "dʱ", "N": "n",
    "p": "p", "ph": "pʰ", "b": "b", "bh": "bʱ", "m": "m",
    "y": "j", "r": "r", "l": "l", "v": "ʋ",
    "s": "s", "sh": "ʃ", "S": "ʂ", "h": "ɦ",
    "ks": "kʂ", "jn": "ɡɲ", "tr": "t̪r",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def is_valid_token(tok: str) -> bool:
    return tok in VALID


def validate_sequence(seq) -> bool:
    """Every token in seq must be a canonical token."""
    return all(is_valid_token(t) for t in seq)


def to_ipa(tokens) -> str:
    out = []
    for t in tokens:
        out.append(TO_IPA.get(t, t))
    return " ".join(out)
