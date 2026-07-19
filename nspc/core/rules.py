# -*- coding: utf-8 -*-
"""
nspc/core/rules.py
=====================================================================
The G2P compiler: Devanagari word -> canonical phone tokens (Phase 1).

It combines:
  (1) orthographic pre-normalization + tag inference  (normalize.py)
  (2) the Unified Priority Rule U5 for final-schwa    (port of u5_reference)
  (3) principled segmental realization:
        - single consonant -> token (+ inherent /a/ unless dead)
        - virama conjunct clusters -> mapped via CLUSTER_MAP (क्ष, त्र, ज्ञ, ...)
        - matras -> vowels
        - anusvara/chandrabindu -> nasalization
  (4) deterministic trace (SPEC §12)

The validated core is the final-schwa decision (U5). Segmental mapping here
is the principled, 1:1-with-orthography realization; it is NOT a black box.
Every step is logged in the trace.

All output tokens are canonical (inventory.py). Adapters translate later.
"""
import unicodedata
from . import normalize as _nz
from . import inventory as _inv

VI_RAMA = "\u094d"

# ---------------------------------------------------------------------------
# Matra (dependent vowel) -> canonical vowel token
# ---------------------------------------------------------------------------
MATRA_TO_VOWEL = {
    "\u093e": "a:",   # ा  -> a: (long vowel)
    "\u093f": "i",    # ि  -> i
    "\u0940": "i:",   # ी  -> i:
    "\u0941": "u",    # ु  -> u
    "\u0942": "u:",   # ू  -> u:
    "\u0943": "r~",   # ृ  -> r~ (tatsama)
    "\u0947": "e",    # े  -> e
    "\u0948": "e",    # ै  -> e  (ai realized as e in Nepali)
    "\u094b": "o",    # ो  -> o
    "\u094c": "au",   # ौ  -> au  (au-kar; e.g. सम्झौता -> samjhauta)
}

# Independent vowels (word-initial)
INDEP_VOWEL = {
    "\u0905": "a",   # अ
    "\u0906": "a:",  # आ
    "\u0907": "i",   # इ
    "\u0908": "i:",  # ई
    "\u0909": "u",   # उ
    "\u090a": "u:",  # ऊ
    "\u090b": "r~",  # ऋ
    "\u090f": "e",   # ए
    "\u0910": "o",   # ऐ (ai->e handled below; ए is e)
}

# ---------------------------------------------------------------------------
# Single consonant base -> canonical token
# ---------------------------------------------------------------------------
CONSONANT_BASE = {
    "\u0915": "k", "\u0916": "kh", "\u0917": "g", "\u0918": "gh", "\u0919": "ng",
    "\u091a": "c", "\u091b": "ch", "\u091c": "j", "\u091d": "jh", "\u091e": "ny",
    "\u091f": "t", "\u0920": "th", "\u0921": "d", "\u0922": "dh", "\u0923": "n",
    "\u0924": "T", "\u0925": "Th", "\u0926": "D", "\u0927": "Dh", "\u0928": "N",
    "\u092a": "p", "\u092b": "ph", "\u092c": "b", "\u092d": "bh", "\u092e": "m",
    "\u092f": "y", "\u0930": "r", "\u0932": "l", "\u0935": "w", "\u0938": "s",
    "\u0936": "sh", "\u0937": "S", "\u0939": "h",
}

# Conjunct clusters (dead C + live C) -> canonical token(s). These are the
# principled multi-char realizations (R7). A conjunct is formed by a DEAD
# consonant (halanta) joined to a LIVE consonant; the LIVE second consonant
# retains its inherent /a/ (verified native: त्र=tra, प्र=pra, क्र=kra, द्र=dra,
# श्र=shra, स्त=sta, स्म=sma, क्ष=ksha, ज्ञ=gyan/gya). So every conjunct here
# emits the second consonant PLUS an 'a', unless the orthography already
# carries an explicit matra after the conjunct (handled by the segmenter), in
# which case the matra supplies the vowel and no trailing 'a' is added.
CLUSTER_MAP = {
    ("\u0915", "\u094d", "\u0937"): ["k", "sh", "a"],   # क्ष -> ksha
    ("\u091c", "\u094d", "\u0944"): ["g", "y"],   # ज्ञ (ज+्+ञ) -> gy (ज्ञान=gyan)
    ("\u091c", "\u094d", "\u091e"): ["g", "y"],   # ज्ञ alt
    ("\u0924", "\u094d", "\u0930"): ["t", "r", "a"],   # त्र -> tra
    ("\u0936", "\u094d", "\u0930"): ["sh", "r", "a"],  # श्र -> shra
    ("\u0938", "\u094d", "\u0924"): ["s", "T", "a"],   # स्त -> sta
    ("\u0938", "\u094d", "\u0924", "\u094d", "\u0930"): ["s", "t", "r", "a"],  # स्त्र -> stra (stacked conjunct)
    ("\u0938", "\u094d", "\u092e"): ["s", "m", "a"],   # स्म -> sma
    ("\u0926", "\u094d", "\u0930"): ["D", "r", "a"],   # द्र -> dra
    ("\u0915", "\u094d", "\u0930"): ["k", "r", "a"],   # क्र -> kra
    ("\u0917", "\u094d", "\u0930"): ["g", "r", "a"],   # ग्र -> gra
    ("\u092a", "\u094d", "\u0930"): ["p", "r", "a"],   # प्र -> pra
    ("\u092a", "\u094d", "\u0930", "\u0947"): ["p", "r", "e"],  # प्रे -> pre (matra replaces र's अ)
}

# Nasalization markers
ANUSVARA = "\u0902"      # ं
CHANDRABINDU = "\u0901"  # ँ
VISARGA = "\u0903"      # ः

# Anusvara (ं) -> nasal consonant by place of the FOLLOWING consonant
# (Sanskrit anunasika sandhi; phonetically realized in Nepali). Maps a
# canonical consonant token to the nasal it triggers.
_ANUSVARA_NASAL = {
    # velar
    "k": "ng", "kh": "ng", "g": "ng", "gh": "ng", "ng": "ng",
    # palatal
    "c": "ny", "ch": "ny", "j": "ny", "jh": "ny", "ny": "ny",
    # retroflex
    "t": "N", "th": "N", "d": "N", "dh": "N", "n": "N",
    # dental
    "T": "n", "Th": "n", "D": "n", "Dh": "n", "N": "n",
    # labial
    "p": "m", "ph": "m", "b": "m", "bh": "m", "m": "m",
    # semivowels / approximants / sibilants / h
    "y": "n", "r": "n", "l": "n", "w": "n",
    "s": "n", "sh": "n", "S": "n", "h": "n",
    # multi-char conjunct tokens: assimilate by their leading place
    "ks": "ng", "jn": "ny", "tr": "N",
}

# Postpositions / derivational suffixes that trigger R7 join-schwa deletion
# when attached to a host stem (verified native: the JOIN schwa drops, the
# suffix keeps its own final अ). Longest-first for greedy matching. Both
# नुक्ता and plain-u forms are included (corpus uses हरु, not हरू).
_POSTPOSITIONS = [
    "जस्तै", "आदि", "वाला", "दार", "सँगै", "पछि", "अघि", "भरि", "सम्म",
    "हरू", "हरु", "सँग", "तिर", "बाट", "मा", "ले", "को", "का", "पनि", "सित",
    "पटक", "पल्ट", "पति", "बिना", "सँग", "लाई",
]
_POSTPOS_SET = set(_POSTPOSITIONS)

# Valid MEDIAL consonant clusters (C1 + C2) where the inherent /a/ of C1 is
# deleted (the pair forms a single onset/cluster in Nepali). R7-general:
# principled cluster inventory, not per-word. Currently covers the
# fricative+stop class (श/ष + stop -> श्प, ष्ट, ...), verified native
# (आकाशपति -> a-kas-pa-ti). Extended conservatively to avoid over-deletion.
_FRICATIVE = {"\u0936", "\u0937"}   # श (palatal fricative), ष (retroflex fricative)
_STOP = {"\u0915", "\u0916", "\u0917", "\u0918",  # क ख ग घ
         "\u091f", "\u0920", "\u0921", "\u0922",  # ट ठ ड ढ
         "\u0924", "\u0925", "\u0926", "\u0927",  # त थ द ध
         "\u092a", "\u092b", "\u092c", "\u092d"}  # प फ ब भ


def _medial_cluster(c1, c2):
    """True if C1 + C2 forms a valid medial cluster (delete C1's schwa).

    NOTE: a blanket 'fricative + stop' rule was REMOVED. Conjuncts are written
    with an explicit virama (e.g. स्क = स्+क) and handled by CLUSTER_MAP; a bare
    fricative+stop sequence without virama is NOT a native cluster (e.g. the
    foreign name शकिरा = sha-ki-ra, श keeps its inherent /a/). Native post-स
    words (आकाशको, देशबाट, ...) keep their fricative's /a/ via the host-final
    path, not this rule.
    """
    return False


def _is_consonant_base(cp):
    return cp in CONSONANT_BASE


def _next_consonant_token(cps, i):
    """Return the canonical consonant token immediately following position i,
    skipping any virama (conjunct join) and matras, stopping at the next base
    consonant. Used by the anusvara assimilation rule. Returns None if none."""
    j = i + 1
    n = len(cps)
    while j < n:
        cp = cps[j]
        if cp == VI_RAMA:
            j += 1
            continue
        if _is_matra(cp):
            j += 1
            continue
        if _is_consonant_base(cp):
            return CONSONANT_BASE[cp]
        # skip other marks (chandrabindu/anusvara/visarga) and move on
        j += 1
    return None


def _is_matra(cp):
    return cp in MATRA_TO_VOWEL


def _cluster_key(cps, i):
    """Build a cluster key from position i if a conjunct starts there."""
    for length in (5, 4, 3):
        if i + length <= len(cps):
            key = tuple(cps[i:i + length])
            if key in CLUSTER_MAP:
                return key
    return None


def _segment_raw(word):
    """Standalone orthographic segmentation of `word` (U5 applied, no R7 join
    logic). Used by R7 to inspect a compound HOST's standalone final-vowel
    behaviour. `word` is always shorter than the full compound, so this
    terminates without recursion."""
    toks, _ = segment(word)
    return toks


def segment(word, tags=None):
    """Core: Devanagari word -> list of canonical tokens, applying U5 to the
    FINAL schwa. Returns (tokens, trace_steps).

    This realization is conservative: it maps orthography 1:1 to canonical
    tokens, deleting the inherent /a/ on a FINAL dead or halanta-shape
    consonant per U5. Medial dead consonants (conjuncts) are NOT given an
    inherent vowel.

    R7 (compound-boundary schwa deletion): when a live consonant is the final
    consonant of a HOST that is followed by a known postposition/suffix, its
    inherent /a/ is deleted at the join (e.g. नेपाल+को -> ne-pal-ko, not
    ne-pa-la-ko). The schwa is dropped at the STEM JOIN, not at the suffix's
    own end (postpositions keep their own final अ, verified native).
    """
    s = _nz.canonicalize(word)
    steps = ["NFC: " + s]

    if tags is None:
        tags = _nz.auto_tag(s)

    # --- U5 decision on final schwa -----------------------------------------
    from .u5_reference import u5
    branch, retain, note = u5(s, tags)
    steps.append("U5." + branch + " -> " + ("RETAIN" if retain else "DELETE") +
                 " (" + note + ")")

    cps = list(s)
    out = []

    # Postpositions / derivational suffixes (नामयोगी / सम्बन्धवाचक) are never
    # pronounced in isolation; they always attach to a preceding host word and
    # KEEP their final inherent /a/ (e.g. सँग -> "saga", not "sag"). They are
    # therefore exempt from the C6 final-schwa DELETE that applies to bare nouns.
    is_postposition = (s in _POSTPOS_SET) or \
        any(s.endswith(p) for p in _POSTPOS_SET if len(p) < len(s))
    i = 0
    n = len(cps)

    # R7: find the host-final consonant index if the word ends in a known
    # postposition. The join schwa (host's last consonant's inherent /a/) is
    # deleted when joining -- but ONLY when the host itself, pronounced
    # standalone, already drops that final consonant's inherent /a/ (i.e. the
    # host ends in a halanta/dead consonant). E.g. नेपाल -> nepal (ल drops),
    # so नेपालको -> nepalko (no extra schwa); साउन -> saun (न drops), so
    # साउनलाई -> saunlai. But म -> ma (लाई keeps its /a/), so मलाई -> malai
    # (the host's final /a/ is retained, NOT deleted at the join).
    join_idx = -1
    host_drops_final_a = False
    for suf in sorted(_POSTPOS_SET, key=len, reverse=True):
        if s.endswith(suf) and len(s) > len(suf):
            host = s[:len(s) - len(suf)]
            for j in range(len(host) - 1, -1, -1):
                if _is_consonant_base(host[j]) and \
                        (j + 1 >= len(host) or host[j + 1] != VI_RAMA):
                    join_idx = j
                    break
            # Determine the host's standalone final-vowel behaviour. The host
            # KEEPS its final inherent /a/ at the join iff, pronounced standalone,
            # it retains its final schwa per U5 — UNLESS the host is a single
            # live consonant (e.g. म -> "ma"), which always keeps its inherent
            # /a/ regardless of the C6 default. Examples:
            #   म     -> ma     (single live C, keeps) -> मलाई   = malai
            #   घर    -> ghar   (U5 RETAIN, keeps)      -> घरलाई  = gharlai
            #   यस    -> yas    (U5 RETAIN, keeps)      -> यसलाई  = yaslai
            #   नेपाल -> nepal  (U5 DELETE, drops)      -> नेपालको = nepalko
            #   साउन  -> saun   (U5 DELETE, drops)      -> साउनलाई = saunlai
            #   करण   -> karan  (U5 DELETE, drops)      -> करणबाट = karanbata
            from .u5_reference import u5 as _u5
            from .normalize import auto_tag as _auto_tag
            _, _host_retain, _ = _u5(host, _auto_tag(host))
            # The host's final schwa is deleted at the join iff the host,
            # pronounced STANDALONE, deletes its final schwa (U5 retain=False).
            # This covers monosyllabic hosts like उस/कस/जस/उन (final स/न drops)
            # as well as polysyllabic ones (नेपाल/साउन). Hosts that retain their
            # final अ standalone (म=halo, घर=HALANTA_FINAL deletes so drops too,
            # यस=RETAIN_FINAL keeps) behave accordingly: मलाई=malai (kept),
            # यसले=yasale (kept, यस retains), घरलाई=gharlai (घर drops standalone).
            host_drops_final_a = not _host_retain
            break

    while i < n:
        cp = cps[i]

        # 1) independent vowel (initial)
        if cp in INDEP_VOWEL:
            out.append(INDEP_VOWEL[cp])
            i += 1
            continue

        # 2) conjunct cluster?
        ckey = _cluster_key(cps, i)
        if ckey is not None:
            tokens = list(CLUSTER_MAP[ckey])
            # If the conjunct is immediately followed by a dependent vowel
            # (matra), that matra REPLACES the conjunct's inherent /a/ (e.g.
            # त्र + ई -> "tri", not "trai"; प्र + े -> "pre", not "prae"). Drop
            # the trailing 'a' we would otherwise have emitted so the matra
            # (handled in step 4) supplies the vowel instead.
            nxt = cps[i + len(ckey)] if i + len(ckey) < n else None
            if nxt is not None and _is_matra(nxt) and tokens and tokens[-1] == "a":
                tokens.pop()
            out.extend(tokens)
            i += len(ckey)
            continue

        # 3) consonant base
        if _is_consonant_base(cp):
            out.append(CONSONANT_BASE[cp])
            nxt = cps[i + 1] if i + 1 < n else None
            if nxt == VI_RAMA:
                # dead consonant (halanta): no inherent vowel; skip virama
                i += 2
                continue
            if nxt is not None and _is_matra(nxt):
                # followed by a matra: the matra supplies the vowel, so do
                # NOT add the inherent 'a'. The matra is emitted in step 4.
                i += 1
                continue
            # live consonant with inherent /a/ UNLESS it is the FINAL consonant
            # and U5 decided DELETE (C6/C0/C1-Lneg), OR it is the host-final
            # consonant at a compound join (R7), OR it forms a medial cluster
            # with the following consonant (R7-general: fricative+stop etc.).
            is_final = (i == n - 1)
            medial = False
            if not (is_final and not retain) and i != join_idx:
                # next consonant after this one's inherent /a/ (skip a matra)
                j = i + 1
                while j < n and (_is_matra(cps[j]) or cps[j] in (ANUSVARA, CHANDRABINDU)):
                    j += 1
                if j < n and _is_consonant_base(cps[j]):
                    medial = _medial_cluster(cp, cps[j])
            if (is_final and not retain and not is_postposition) or \
                    (i == join_idx and host_drops_final_a) or medial:
                pass  # suppress inherent /a/
            else:
                out.append("a")
            i += 1
            continue

        # 4) matra (dependent vowel)
        if _is_matra(cp):
            out.append(MATRA_TO_VOWEL[cp])
            i += 1
            continue

        # 5) nasalization
        if cp == CHANDRABINDU:
            # Chandrabindu (ँ): PURE vowel nasalization. No consonant is
            # realized; the preceding vowel is marked nasal (~). e.g. सँ -> sa~,
            # सँगै -> sa~ + gai = "sagai" (न silent). Rule-based, distinct from
            # anusvara below.
            if out and out[-1] in _inv.VOWELS and not out[-1].endswith("~"):
                out[-1] = out[-1] + "~"
            else:
                out.append("a~")  # rare: standalone chandrabindu
            i += 1
            continue
        if cp == ANUSVARA:
            # Anusvara (ं): realized as a NASAL CONSONANT whose place matches the
            # FOLLOWING consonant (Sanskrit anunasika sandhi, phonetic in Nepali).
            #   velar  (कखगघङ)        -> ng   (संगीत = sangit)
            #   palatal(चछजझञ)        -> ny   (संज्ञ = sanj~nya)
            #   retroflex(टठडढण)       -> N    (संढ = saNdh..)
            #   dental (तथदधन)         -> n    (संतति = santati)
            #   labial (पफबभम)         -> m    (संभव = sambhav)
            #   semi/appoint(yrlwशषसह)-> n    (संस्कृति = sanskriti)
            # If no following consonant, default to 'n' (rare, word-final ं).
            nxt_cons = _next_consonant_token(cps, i)
            nasal = _ANUSVARA_NASAL.get(nxt_cons, "n")
            out.append(nasal)
            i += 1
            continue

        if cp == VISARGA:
            # visarga -> /h/ (Sanskrit retention); rare in Nepali
            out.append("h")
            i += 1
            continue

        # 6) unknown char (punctuation/Latin) -> skip (normalize_text handles)
        i += 1

    steps.append("tokens: " + " ".join(out))
    steps.append("final-schwa: " + ("kept" if retain else "deleted"))
    return out, steps


def g2p(word, **etym):
    """Public: word -> canonical tokens. etym passed to auto_tag."""
    s = _nz.NFC(word)
    tags = _nz.auto_tag(s, **etym)
    tokens, steps = segment(s, tags)
    return tokens, tags, steps
