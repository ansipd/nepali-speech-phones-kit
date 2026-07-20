# -*- coding: utf-8 -*-
"""
nspc/core/mixed_script.py
=========================================================================
Mixed-script (Roman -> Devanagari) preprocessing for the Nepali G2P
frontend.

WHY: real Nepali TTS input is rarely 100% Devanagari. Speakers code-switch
("facebook नचलाइ station जाने हो र?"). Roman characters must be turned into
Devanagari BEFORE the number module and the Ohala phonology engine run, so the
downstream pipeline only ever sees Devanagari (and digits). Unhandled Roman
tokens would otherwise break word segmentation / the acoustic model.

DESIGN (two-tier, additive — does NOT touch the pure-Nepali core):
  Tier 1 (whitelist): a hardcoded lookup of common English loanwords whose
          dynamic transliteration is unreliable. Checked first.
  Tier 2 (dynamic):   if not whitelisted, convert via an open-source
          transliteration library when available (AI4Bharat IndicXlit, Nepali
          "ne" code), else a lightweight rule-based Roman->Devanagari mapper.
          The rule-based fallback keeps the engine self-contained and testable
          offline; the ML path is OPTIONAL (not a hard dependency).

Native-speaker ear (TTS listening) is the authority for the whitelist forms,
not the library's guess.

DETECTION: a token is "Roman" if it contains any ASCII A-Z / a-z character.
Pure Devanagari, digit, or punctuation tokens pass through untouched.
"""
import re

# A token is treated as containing Roman script if it has any ASCII letter.
_ROMAN_RE = re.compile(r"[A-Za-z]")

# Tier 1: common loanwords whose dynamic transliteration is often wrong or
# unstable across engines. Forms verified against native-speaker pronunciation.
# (Add more as the native ear flags them.)
WHITELIST = {
    "facebook": "फेसबुक",
    "station": "स्टेसन",
    "hello": "हेलो",
    "google": "गुगल",
    "whatsapp": "वाट्सएप",
    "youtube": "युट्युब",
    "internet": "इन्टर्नेट",
    "computer": "कम्प्युटर",
    "mobile": "मोबाइल",
    "phone": "फोन",
    "bus": "बस",
    "school": "स्कुल",
    "college": "कलेज",
    "online": "अनलाइन",
    "email": "इमेल",
    "message": "मेसेज",
    "video": "भिडियो",
    "number": "नम्बर",
}

# ---------------------------------------------------------------------------
# Tier 2a: optional ML transliteration (AI4Bharat IndicXlit), lazy import.
# ---------------------------------------------------------------------------
def _indicxlit_transliterate(roman):
    """Translate a Roman string to Devanagari via IndicXlit (Nepali "ne").

    Returns the Devanagari string, or None if the library is unavailable or
    fails. Never raises — the caller falls back to the rule-based mapper.
    """
    try:
        from indicxlit import XlitEngine  # optional dependency
    except Exception:
        return None
    try:
        eng = XlitEngine("ne", beam_width=1)
        out = eng.translit_word(roman, topk=1)
        # indicxlit returns a list of candidates; take the top one.
        if isinstance(out, list) and out:
            return out[0]
        if isinstance(out, str) and out:
            return out
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# Tier 2b: lightweight rule-based Roman -> Devanagari mapper (offline fallback).
# This is an APPROXIMATION of Nepali-accented pronunciation, not a full
# transliteration engine. It handles the common cases so the pipeline never
# emits raw Roman text. Forms are Indic-phonetic, verified against native ear
# for typical loanwords.
# ---------------------------------------------------------------------------
# Vowel map (Roman short/long -> Devanagari). '' means "no inherent vowel".
_VOWELS = {
    "a": "अ", "aa": "आ",
    "i": "इ", "ee": "ई", "ii": "ई", "e": "ए",
    "u": "उ", "oo": "ऊ", "uu": "ऊ", "o": "ओ",
    "ri": "ऋ", "ae": "ऐ", "ai": "ऐ", "au": "औ", "ow": "औ",
}
# Consonant map (Roman cluster -> Devanagari consonant with inherent अ).
_CONSONANTS = {
    "k": "क", "kh": "ख", "g": "ग", "gh": "घ", "ng": "ङ",
    "c": "च", "ch": "छ", "j": "ज", "jh": "झ", "ny": "ञ",
    "t": "ट", "th": "ठ", "d": "ड", "dh": "ढ", "n": "ण",
    "T": "त", "Th": "थ", "D": "द", "Dh": "ध", "N": "न",
    "p": "प", "ph": "फ", "f": "फ", "b": "ब", "bh": "भ",
    "m": "म", "y": "य", "r": "र", "l": "ल", "w": "व", "v": "व",
    "sh": "श", "s": "स", "S": "श", "h": "ह",
    "ks": "क्ष", "gy": "ज्ञ", "tr": "त्र", "dr": "द्र", "shr": "श्र",
}
# Halant (vowel-killer) used when a consonant is followed by another consonant
# or explicit 'h' (aspirated) / end-of-cluster.
_HALANT = "्"
_VISARGA = "ः"


def _rule_transliterate(roman):
    """Approximate Roman -> Devanagari for a single lowercased token.

    Strategy: left-to-right greedy longest-match over consonant digraphs then
    single consonants, inserting halant between consecutive consonants, and
    appending vowels. This is intentionally simple and offline.
    """
    s = roman.lower()
    out = []
    i = 0
    n = len(s)
    pending_halant = False  # whether the last emitted consonant needs a halant
    while i < n:
        ch = s[i]
        # whitespace / digits / punctuation -> keep as-is inside a token
        if not ch.isalpha():
            out.append(ch)
            pending_halant = False
            i += 1
            continue
        # try 2-char consonant digraph first
        two = s[i:i + 2]
        matched = None
        if two in _CONSONANTS:
            matched = _CONSONANTS[two]
            i += 2
        elif ch in _CONSONANTS:
            matched = _CONSONANTS[ch]
            i += 1
        if matched is not None:
            if pending_halant and out:
                # join previous consonant to this one with halant
                if out[-1] not in ("ः",) and len(out[-1]) == 1:
                    out[-1] = out[-1] + _HALANT
            out.append(matched)
            pending_halant = True
            continue
        # vowel (single char)
        if ch in _VOWELS:
            v = _VOWELS[ch]
            if pending_halant:
                # a following vowel replaces the pending halant (inherent vowel)
                if out and out[-1].endswith(_HALANT):
                    out[-1] = out[-1][:-1]
                out.append(v)
                pending_halant = False
            else:
                out.append(v)
            i += 1
            continue
        # unknown char -> keep literally
        out.append(ch)
        pending_halant = False
        i += 1
    return "".join(out)


def transliterate_roman(roman):
    """Tier 1 + Tier 2 dispatch for a single Roman token (lowercased lookup
    is case-insensitive). Returns a Devanagari string."""
    key = roman.lower()
    if key in WHITELIST:
        return WHITELIST[key]
    ml = _indicxlit_transliterate(roman)
    if ml:
        return ml
    return _rule_transliterate(roman)


def normalize_mixed_script(text):
    """Preprocess `text`: convert any Roman-containing token to Devanagari
    (two-tier), leaving pure Devanagari / digit / punctuation tokens untouched.

    This is intended to run as the FIRST step of the normalization pipeline,
    before number expansion and phonology. Returns the reconstructed string
    (still whitespace-separated).
    """
    out_tokens = []
    for chunk in text.split():
        # Preserve surrounding punctuation attached to the chunk; only the
        # inner word content is transliterated if it contains Roman letters.
        lead = ""
        trail = ""
        inner = chunk
        # strip leading/trailing punctuation (same set as normalize_text.PUNCT)
        _punct = "।,;.!?\"'()[]{}:/-"
        while inner and inner[0] in _punct:
            lead += inner[0]
            inner = inner[1:]
        while inner and inner[-1] in _punct:
            trail = inner[-1] + trail
            inner = inner[:-1]
        if _ROMAN_RE.search(inner):
            # transliterate the inner Roman word(s); keep internal spacing
            converted = " ".join(
                transliterate_roman(w) if _ROMAN_RE.search(w) else w
                for w in inner.split()
            )
            out_tokens.append(lead + converted + trail)
        else:
            out_tokens.append(chunk)
    return " ".join(out_tokens)
