# -*- coding: utf-8 -*-
"""
nspc/core/numbers.py
=========================================================================
Nepali number verbalization (text normalization, R1.1/R1.2 pre-G2P stage).

Converts integer / decimal digit strings (Devanagari ०-९ or ASCII 0-9)
into space-separated Nepali WORD tokens, which are then handed off to the
existing word-level G2P (Ohala + R7 boundary rules). This module only does
digit -> spelled-out Devanagari text; it never emits phones.

Design notes (per NSPC-Kit methodology: rule-based, native-ear authority):

1. Base cardinals 0-99 are an idiosyncratic lookup table (each number 1-99
   has its own word in Nepali, unlike English composition). This table and
   the compositional सय/हजार/लाख/करोड logic are ADAPTED from the Ampixa
   ``nepa-newa-text-frontend`` project (MIT licensed, code in
   ``nepali_frontend/``). See https://github.com/Ampixa/nepa-newa-text-frontend
   and its LICENSE (MIT). The 0-99 forms were cross-referenced against
   Wikipedia "Numbers in Nepali language", imnepal.com, omniglot.com.

2. Year vs count: in modern spoken Nepali the year 2026 and the count 2,026
   are pronounced identically -> "दुई हजार छब्बीस". We therefore use standard
   thousand/lakh/crore math for ALL numbers >= 2000 (never "बिस सय छब्बीस").
   For 1100-1999 we add an OPTIONAL context rule: if the number is immediately
   followed by a date keyword (साल, वर्ष, सम्म, को) it groups by hundreds
   ("उन्नाइस सय नब्बे"); otherwise standard math ("एक हजार नौ सय नब्बे").

3. Decimals (trigger on "."): integer part verbalized normally; fractional
    digits read ONE BY ONE (12.55 -> "बाह्र पोइन्ट पाँच पाँच", NOT grouped).
    Default separator is the English loanword "पोइन्ट" (modern spoken Nepali);
   pass formal=True to use the formal "दशमलव" for news/official text.

  4. Phonology integration: output is Devanagari word tokens only. The caller
     feeds each token through the existing engine (lexicon.process / rules.segment);
  5. Mobile-number fallback: a 10-digit run starting with 9 (ASCII) or ९
     (Devanagari) is read digit-by-digit (e.g. 9849658494 -> नौ आठ चार नौ छ
     पाँच आठ चार नौ चार), bypassing all compositional math.
  6. Fractions ("a/b"): read as "a बाइ b" (modern spoken Nepali), e.g. १/२ ->
     एक बाइ दुई. Both sides use the normal number rules.
  7. Percentages ("N%"): the "%" is consumed and replaced by "प्रतिशत", e.g.
     50% -> पचास प्रतिशत.
  Ordinals are NOT generated from digits: Nepali writes ordinals as full
  Devanagari words (पहिलो, दोस्रो, पाँचौँ...), which the G2P/lexicon already
  handle, so no ordinal table is needed in the number module.
  No changes needed to the pronunciation engine.

Not yet covered (out of scope for v0): ordinals, currency (रुपैयाँ),
percentages, fractions (१/२). Can be added as separate functions later.
"""

from __future__ import annotations

import re

# Punctuation that does NOT separate words (kept attached). Used by
# normalize_numbers_in_text to decide whether to insert a space after a
# glued number+keyword (e.g. 1990साल -> "उन्नाइस सय नब्बे साल").
PUNCT = set("।,;.!?\"'()[]{}:/-")

# ---------------------------------------------------------------------------
# 0-99 cardinals (idiosyncratic per Nepali grammar).
# Adapted from Ampixa/nepa-newa-text-frontend (MIT). See module docstring.
# ---------------------------------------------------------------------------
CARDINALS_0_99 = {
    0: "शून्य",
    1: "एक",
    2: "दुई",
    3: "तीन",
    4: "चार",
    5: "पाँच",
    6: "छ",
    7: "सात",
    8: "आठ",
    9: "नौ",
    10: "दश",
    11: "एघार",
    12: "बाह्र",
    13: "तेह्र",
    14: "चौध",
    15: "पन्ध्र",
    16: "सोह्र",
    17: "सत्र",
    18: "अठार",
    19: "उन्नाइस",
    20: "बीस",
    21: "एक्काइस",
    22: "बाइस",
    23: "तेईस",
    24: "चौबिस",
    25: "पच्चिस",
    26: "छब्बिस",
    27: "सत्ताइस",
    28: "अठ्ठाईस",
    29: "उनन्तिस",
    30: "तीस",
    31: "एकत्तिस",
    32: "बत्तिस",
    33: "तेत्तिस",
    34: "चौँतिस",
    35: "पैँतिस",
    36: "छत्तिस",
    37: "सैँतीस",
    38: "अठतीस",
    39: "उनन्चालीस",
    40: "चालीस",
    41: "एकचालीस",
    42: "बयालीस",
    43: "त्रियालीस",
    44: "चवालीस",
    45: "पैँतालीस",
    46: "छयालीस",
    47: "सच्चालीस",
    48: "अठचालीस",
    49: "उनन्चास",
    50: "पचास",
    51: "एकाउन्न",
    52: "बाउन्न",
    53: "त्रिपन्न",
    54: "चउन्न",
    55: "पचपन्न",
    56: "छपन्न",
    57: "सन्ताउन्न",
    58: "अन्ठाउन्न",
    59: "उनन्साठी",
    60: "साठी",
    61: "एकसट्ठी",
    62: "बयसट्ठी",
    63: "त्रिसट्ठी",
    64: "चौंसट्ठी",
    65: "पैंसट्ठी",
    66: "छयसट्ठी",
    67: "सतसट्ठी",
    68: "अठसट्ठी",
    69: "उनन्सत्तरी",
    70: "सत्तरी",
    71: "एकहत्तर",
    72: "बहत्तर",
    73: "त्रिहत्तर",
    74: "चौहत्तर",
    75: "पचहत्तर",
    76: "छयहत्तर",
    77: "सतहत्तर",
    78: "अठहत्तर",
    79: "उनासी",
    80: "असी",
    81: "एकासी",
    82: "बयासी",
    83: "त्रियासी",
    84: "चौरासी",
    85: "पचासी",
    86: "छयासी",
    87: "सतासी",
    88: "अठासी",
    89: "उनान्नब्बे",
    90: "नब्बे",
    91: "एकान्नब्बे",
    92: "बयान्नब्बे",
    93: "त्रियान्नब्बे",
    94: "चौरान्नब्बे",
    95: "पन्चानब्बे",
    96: "छयान्नब्बे",
    97: "सन्तान्नब्बे",
    98: "अन्ठान्नब्बे",
    99: "उनान्सय",
}

HUNDRED = "सय"
THOUSAND = "हजार"
LAKH = "लाख"
CRORE = "करोड"

# Date / year context keywords (used only for the 1100-1999 optional rule).
_DATE_KEYWORDS = {"साल", "वर्ष", "सम्म", "को"}

# Decimal separator word(s).
_POINT_MODERN = "पोइन्ट"
_POINT_FORMAL = "दशमलव"

# Fraction "by" word and percentage word (modern spoken Nepali).
_FRACTION_BY = "बाइ"      # "a/b" -> "a बाइ b"  (e.g. १/२ -> एक बाइ दुई)
_PERCENT_WORD = "प्रतिशत"  # "50%" -> "पचास प्रतिशत"

DEVA_DIGIT_TO_INT = {
    "०": 0, "१": 1, "२": 2, "३": 3, "४": 4,
    "५": 5, "६": 6, "७": 7, "८": 8, "९": 9,
}

# Matches a numeric run (Devanagari or ASCII digits) that may contain
# grouping separators (commas, Devanagari commas U+0964/U+0965) and an
# optional single decimal point, and an optional leading minus sign.
# clean_numeric() strips separators and turns a leading minus into माइनस.
# e.g. "-15", "1,50,000", "१,५०,०००.५" match as one run. A trailing "%"
# is consumed so the percentage word can be appended (see repl()).
_DIGIT_RE = re.compile(
    r"-?[०-९0-9]+(?:[,\u0964\u0965]?[०-९0-9]+)*(?:\.[०-९0-9]+)?%?"
)

# Fraction "a/b": two integer runs joined by a solidus. Consumed as a whole so
# the number module reads both sides (e.g. "१/२" -> "एक बाइ दुई"). A fraction
# run is matched and substituted BEFORE the plain digit run below.
_FRACTION_RE = re.compile(
    r"-?[०-९0-9]+(?:[,\u0964\u0965]?[०-९0-9]+)*/-?[०-९0-9]+(?:[,\u0964\u0965]?[०-९0-9]+)*"
)

# Thousand-separators / grouping marks to strip before parsing. Nepali uses
# the lakh/crore comma system (1,50,000) which must be removed so the math
# sees the bare integer. Covers ASCII comma, Devanagari comma (०-पूर्णविराम
# U+0964 / U+0965), and NBSP.
_SEP_CHARS = {" ", ",", "\u0964", "\u0965", "\u00a0", "\u2009", "_"}
_SIGN_WORD = "माइनस"  # Nepali for "minus" (negative numbers)
_ASCII_DIGITS = set("0123456789")
_DEVA_DIGITS = set(DEVA_DIGIT_TO_INT.keys())  # ०१२३४५६७८९


def clean_numeric(s):
    """Normalize a raw numeric token for parsing.

    - strips grouping separators (commas, Devanagari commas, spaces, NBSP)
    - extracts a leading '-' (or Unicode minus) sign -> returns (neg, digits)
    - normalizes a bare fraction ".5" -> "0.5" (so the integer part is शून्य)

    Returns (is_negative, cleaned_string) where cleaned_string is a bare
    digit run with optional single dot, or (False, "") if nothing parseable.
    """
    if not s:
        return False, ""
    s = s.strip()
    neg = False
    # Unicode minus signs and ASCII hyphen/minus
    if s[0] in ("-", "\u2212", "\u2013", "\u2014"):
        neg = True
        s = s[1:].strip()
    # strip separators
    s = "".join(ch for ch in s if ch not in _SEP_CHARS)
    if not s:
        return neg, ""
    # bare fraction -> 0.<frac>
    if s.startswith("."):
        s = "0" + s
    return neg, s


# ---------------------------------------------------------------------------
# Low-level parsing
# ---------------------------------------------------------------------------
def parse_int(s):
    """Parse a pure integer digit string (Devanagari or ASCII) into an int.
    Returns None if `s` contains any non-digit character."""
    if not s:
        return None
    out = 0
    for ch in s:
        if ch in DEVA_DIGIT_TO_INT:
            out = out * 10 + DEVA_DIGIT_TO_INT[ch]
        elif ch.isdigit():
            out = out * 10 + int(ch)
        else:
            return None
    return out


def parse_digit_char(ch):
    """Map a single Devanagari or ASCII digit char to its int value."""
    if ch in DEVA_DIGIT_TO_INT:
        return DEVA_DIGIT_TO_INT[ch]
    return int(ch)


# ---------------------------------------------------------------------------
# Cardinal verbalization (compositional, standard Nepali math)
# ---------------------------------------------------------------------------
def cardinal(n, _context=None):
    """Return the Nepali word tokens (list of Devanagari strings) for a
    non-negative integer `n`, using standard सय/हजार/लाख/करोड math.

    `_context` (internal) carries the date-keyword flag for the 1100-1999
    optional grouping rule; callers should not pass it.
    """
    if n < 0:
        raise ValueError("negative numbers not supported in v0")
    if n < 100:
        return [CARDINALS_0_99[n]]
    if n < 1000:
        h, rem = divmod(n, 100)
        out = cardinal(h) + [HUNDRED]
        if rem:
            out += cardinal(rem)
        return out
    if n < 100_000:
        t, rem = divmod(n, 1000)
        out = cardinal(t) + [THOUSAND]
        if rem:
            out += cardinal(rem)
        return out
    if n < 10_000_000:
        l, rem = divmod(n, 100_000)
        out = cardinal(l) + [LAKH]
        if rem:
            out += cardinal(rem)
        return out
    c, rem = divmod(n, 10_000_000)
    out = cardinal(c) + [CRORE]
    if rem:
        out += cardinal(rem)
    return out


def _cardinal_with_year_rule(n, is_date):
    """Cardinal for 1100-1999 with the optional date-context grouping.

    - is_date True  -> group by hundreds: 1990 -> उन्नाइस सय नब्बे
    - is_date False -> standard math:     1990 -> एक हजार नौ सय नब्बे
    Numbers outside 1100-1999 ignore `is_date` (standard math).
    """
    if 1100 <= n <= 1999 and is_date:
        h, rem = divmod(n, 100)
        out = cardinal(h) + [HUNDRED]
        if rem:
            out += cardinal(rem)
        return out
    return cardinal(n)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def verbalize_int(s, is_date=False):
    """Verbalize a single integer digit string (Devanagari or ASCII).

    Handles separators (commas), a leading minus (-> माइनस), and Devanagari
    digits. `is_date`: when True and the value is in 1100-1999, groups by
    hundreds (year-style). Returns a list of Devanagari word tokens, or []
    if `s` is not a parseable integer.
    """
    neg, cleaned = clean_numeric(s)
    n = parse_int(cleaned)
    if n is None:
        return []
    out = _cardinal_with_year_rule(n, is_date)
    if neg:
        out = [_SIGN_WORD] + out
    return out


def verbalize_decimal(s, formal=False):
    """Verbalize a decimal digit string "INT.FRAC" (Devanagari or ASCII).

    Handles separators, leading minus, and a bare fraction (".5" -> शून्य).
    Integer part: normal cardinal. Fractional digits: read ONE BY ONE.
    Separator: "पोइन्ट" (modern, default) or "दशमलव" (formal=True).
    Returns list of Devanagari word tokens, or [] on parse failure.
    """
    neg, cleaned = clean_numeric(s)
    if "." not in cleaned:
        return verbalize_int(cleaned, is_date=False) if not neg else \
            [_SIGN_WORD] + verbalize_int(cleaned, is_date=False)
    int_part, frac_part = cleaned.split(".", 1)
    n_int = parse_int(int_part)
    if n_int is None:
        return []
    point = _POINT_FORMAL if formal else _POINT_MODERN
    out = cardinal(n_int)
    out.append(point)
    for ch in frac_part:
        d = parse_digit_char(ch)
        out.append(CARDINALS_0_99[d])
    if neg:
        out = [_SIGN_WORD] + out
    return out


def verbalize_mobile(s):
    """Verbalize a 10-digit mobile phone number string (Devanagari or ASCII).

    Bypasses ALL compositional math (thousand/lakh/crore) and 0-99 pairing.
    Each digit is mapped to its standalone name from the 0-9 base table and
    the words are joined by single spaces.

    Detection (caller responsibility): the input must be exactly 10 digit
    characters starting with '9' (ASCII) or '९' (Devanagari). Returns [] if
    `s` is not a clean 10-digit run.
    """
    digits = [ch for ch in s if ch in _ASCII_DIGITS or ch in _DEVA_DIGITS]
    if len(digits) != 10 or digits[0] not in ("9", "९"):
        return []
    out = []
    for ch in digits:
        d = parse_digit_char(ch)
        out.append(CARDINALS_0_99[d])
    return out


def verbalize_digit_run(s, is_date=False, formal=False):
    """Dispatch on whether `s` contains a decimal point.

    A 10-digit run beginning with '9' (ASCII) or '९' (Devanagari) is treated
    as a mobile phone number and read digit-by-digit (see verbalize_mobile).

    Returns list of Devanagari word tokens (may be empty if unparseable).
    """
    # Mobile-number fallback: exactly 10 digits, leading 9 / ९.
    digit_chars = [ch for ch in s if ch in _ASCII_DIGITS or ch in _DEVA_DIGITS]
    if len(digit_chars) == 10 and digit_chars[0] in ("9", "९"):
        return verbalize_mobile(s)
    neg, cleaned = clean_numeric(s)
    if "." in cleaned:
        return verbalize_decimal(s, formal=formal)
    return verbalize_int(s, is_date=is_date)


def verbalize_fraction(s, formal=False):
    """Verbalize a fraction "A/B" (Devanagari or ASCII digits) as
    "A बाइ B" (modern spoken Nepali, e.g. १/२ -> एक बाइ दुई). Each side is
    verbalized with the normal number rules (compositional math, mobile
    fallback, etc.). Returns [] if `s` is not a fraction shape.
    """
    if "/" not in s:
        return []
    left, right = s.split("/", 1)
    lw = verbalize_digit_run(left, formal=formal)
    rw = verbalize_digit_run(right, formal=formal)
    if not lw or not rw:
        return []
    return lw + [_FRACTION_BY] + rw



def normalize_numbers_in_text(text, formal=False):
    """Replace every digit run (integer or decimal) in `text` with its
    Nepali word form, joined by single spaces. Non-digit content (including
    any Devanagari/ASCII letters and punctuation) is preserved verbatim.

    Date-context grouping (1100-1999) is applied when a digit run is
    immediately followed by a date keyword. Mixes ASCII and Devanagari
    digits transparently.

    NOTE: this is a simple regex substitution. It does not track sentence
    context beyond the immediate next token, so the 1100-1999 date grouping
    only triggers when the keyword is glued/adjacent after the number. For
    full sentence-level context, call `verbalize_*` per token from the
    tokenizer instead.
    """

    def repl(match):
        run = match.group(0)
        # Trailing "%" was consumed by the regex; strip it and append the
        # percentage word.
        is_percent = run.endswith("%")
        if is_percent:
            run = run[:-1]
        # look at the text right after the run for a date keyword
        # (keywords are multi-char: साल, वर्ष, सम्म, को)
        end = match.end()
        after = text[end:] if end < len(text) else ""
        is_date = any(after.startswith(kw) for kw in _DATE_KEYWORDS)
        words = verbalize_digit_run(run, is_date=is_date, formal=formal)
        if not words:
            return match.group(0)
        if is_percent:
            words = words + [_PERCENT_WORD]
        out = " ".join(words)
        # Leading sign (e.g. "-15"): the regex does not consume the sign, so
        # prepend the Nepali word "माइनस" and a space.
        start = match.start()
        if start > 0 and text[start - 1] in ("-", "\u2212", "\u2013", "\u2014"):
            out = _SIGN_WORD + " " + out
        # If the next char is a letter (not space/punct), the original text
        # had the keyword glued to the number (e.g. "1990साल"). Insert a
        # space so the downstream whitespace tokenizer keeps the keyword as
        # its own word ("उन्नाइस सय नब्बे साल").
        if end < len(text) and not text[end].isspace() and text[end] not in PUNCT:
            out = out + " "   # separate last number word from glued keyword
        return out

    # Fractions ("a/b") first, so the "/" is consumed before the plain digit
    # pass would otherwise split it into two separate numbers.
    text = _FRACTION_RE.sub(
        lambda m: " ".join(verbalize_fraction(m.group(0), formal=formal)), text
    )
    return _DIGIT_RE.sub(repl, text).strip()
