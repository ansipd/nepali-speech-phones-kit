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
    "\u0948": "ai",   # ै  -> ai (the Sanskrit diphthong ऐ is ai in Nepali)
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
    "\u0910": "ai",  # ऐ (independent vowel, same as matra ै)
    "\u0913": "o",   # ओ (independent vowel, same as matra ो)
    "\u0914": "au",  # औ (independent vowel, same as matra ौ)
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
    "\u092f": "y", "\u0930": "r", "\u0932": "l", "\u0935": "v", "\u0938": "s",
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
    ("\u091c", "\u094d", "\u091e"): ["g", "y"],   # ज्ञ (ज+्+ञ) -> gy (ज्ञान=gyan)
    ("\u0924", "\u094d", "\u0930"): ["T", "r", "a"],   # त्र -> Tra (dental T)
    ("\u0936", "\u094d", "\u0930"): ["sh", "r", "a"],  # श्र -> shra
    ("\u0938", "\u094d", "\u0924"): ["s", "T", "a"],   # स्त -> sta
    ("\u0938", "\u094d", "\u0924", "\u094d", "\u0930"): ["s", "T", "r", "a"],  # स्त्र -> stra (dental T)
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
    # retroflex (n = retroflex [ɳ])
    "t": "n", "th": "n", "d": "n", "dh": "n", "n": "n",
    # dental (N = dental [n])
    "T": "N", "Th": "N", "D": "N", "Dh": "N", "N": "N",
    # labial
    "p": "m", "ph": "m", "b": "m", "bh": "m", "m": "m",
    # semivowels / approximants / sibilants / h
    "y": "N", "r": "N", "l": "N", "v": "N",
    "s": "N", "sh": "N", "S": "N", "h": "N",
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
    "पटक", "पल्ट", "पति", "बिना", "लाई",
    "कै", "भित्र",
]
_POSTPOS_SET = set(_POSTPOSITIONS)

# Number-compound suffixes (tens bases like चालीस, सट्ठी, हत्तर) that trigger
# R7 join-schwa deletion at the prefix boundary (e.g. अठ + तीस -> अठतीस,
# एक + चालीस -> एकचालीस). Unlike postpositions, these do NOT set
# is_postposition — number words follow C6 default DELETE for final schwa.
# Only longer, unique suffixes are included to avoid false positives.
_NUM_COMPOUND_SUFFIXES = {
    "तीस", "चालीस", "पन्न", "सट्ठी", "हत्तर",
}

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


# Liquids / glides as MEDIAL CODAS: in native compounds C1-liquid-V the liquid
# (र/ल/व/य) is a coda and DROPS its inherent /a/; the vowel belongs to the next
# consonant. See _ohala_internal_schwa.
_LIQUID_GLIDE = {"\u0930", "\u0932", "\u0935", "\u092f"}  # र ल व य
# Matra + nasal diacritics: characters that can follow a consonant WITHOUT
# blocking a join boundary (vowel signs and nasal marks).
_MATRA_NASAL_SET = set(MATRA_TO_VOWEL.keys()) | {ANUSVARA, CHANDRABINDU}


def _ohala_internal_schwa(cps, i, join_idx=None):
    """Internal schwa-deletion for native VC_CV clusters (Ohala-style).

    A consonant at position i DROPS its inherent /a/ when it is preceded
    by a vowel-full consonant (C1) and followed by another consonant (C3) which
    itself is followed by a vowel. The medial /a/ is deleted (coda); the vowel
    is the onset of C3. Applies to ALL consonants, not just liquids — the
    original Ohala (1983) Hindi/Nepali rule: ə -> ∅ / VC_CV.

    Native-compound (stem + suffix), native-confirmed:
        सरकार = स र कार -> sarkar   (स keeps /a/, र coda drops, का=long /a:/)
        तरबार = त र बार -> tarbar   (त keeps, र coda drops)
        सलवार = स ल वार -> salwar   (स keeps, ल coda drops)
        तलवार = त ल वार -> talwar   (त keeps, ल coda drops)

    PROTECTED (liquid KEEPS its /a/ -- it is a syllable peak, not a coda):
        कमल  = क म ल   -> kamal   (ल is word-final -> keeps)
        करण  = क र ण   -> karan   (ण is word-final -> र keeps)
        शकिरा = श कि रा -> shakira (र is immediately followed by its OWN matra
                                 ा -> र is the peak, keeps)
        बन्द  = ब न् द  -> baNDa   (न is a dead conjunct -> keeps; र not liquid)

    Returns True iff the liquid/glide at position i should suppress its /a/.

    The vowel that licenses the deletion must be IMMEDIATELY after C3 (C3 is
    itself vowel-bearing: the next token is a matra or independent vowel, with
    NO other consonant between). This is what separates a true coda
    (स-र-कार: क is vowel-bearing -> र drops) from an intervening cluster
    (प-र-म्प-रा: म is followed by प, not a vowel -> र keeps). It also must NOT
    look past a compound-join boundary (join_idx): a vowel belonging to the
    SUFFIX must not license deletion of a liquid inside the STEM
    (क-ल-म-ले: the े is in ले, past the join -> ल keeps -> kalamle).
    """
    n = len(cps)
    if i <= 0 or i >= n - 1:
        return False
    # Only applies to consonants INSIDE the stem (before a compound join). A
    # suffix-initial liquid (e.g. व in वाला) must keep its /a/ as a peak.
    if join_idx is not None and join_idx >= 0 and i >= join_idx:
        return False
    # C1 = nearest base consonant BEFORE i (skip matras/nasals). e.g. in
    # राज-मार्ग, C1 for ज is र (skip the matra ा at position i-1).
    _c1 = i - 1
    while _c1 >= 0 and (_is_matra(cps[_c1]) or cps[_c1] in (ANUSVARA, CHANDRABINDU)):
        _c1 -= 1
    if _c1 < 0 or not _is_consonant_base(cps[_c1]):
        return False
    # find C3 = next base consonant after i (skip matras/nasals on the liquid)
    j = i + 1
    while j < n and (_is_matra(cps[j]) or cps[j] in (ANUSVARA, CHANDRABINDU)):
        j += 1
    if j >= n or not _is_consonant_base(cps[j]):
        return False  # liquid is immediately followed by its own vowel -> peak
    # C3 must be vowel-bearing: the very next token after C3 must be a
    # matra/indep vowel (explicit vowel), OR another live consonant (meaning
    # C3 has inherent अ). This second case is what triggers deletion in
    # compounds like राज-बहादुर (ज's schwa deleted before ब, which has
    # inherent अ followed by ह). C3 at word-end does NOT trigger deletion
    # (e.g. क-म-ल: the म keeps its /a/). Also within the same word unit
    # (before any compound join).
    k = j + 1
    if k < n and (join_idx < 0 or k < join_idx):
        if _is_matra(cps[k]) or cps[k] in INDEP_VOWEL:
            return True   # explicit vowel on C3 (aa, i, u, e, o, ai, au)
        if _is_consonant_base(cps[k]):
            return True   # C3 has inherent अ (followed by another consonant)
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
    # R7 recursive: find ALL suffix/postposition boundaries from the tail inward
    # (e.g. जवानहरूकै has boundaries at न before हरू and र before कै).
    join_idxs: set[int] = set()
    host_drops: dict[int, bool] = {}
    _remaining = s
    while True:
        matched = False
        for suf in sorted(_POSTPOS_SET, key=len, reverse=True):
            if _remaining.endswith(suf) and len(_remaining) > len(suf):
                _host = _remaining[:len(_remaining) - len(suf)]
                _join = -1
                for j in range(len(_host) - 1, -1, -1):
                    if _is_consonant_base(_host[j]) and \
                            (j + 1 >= len(_host) or _host[j + 1] != VI_RAMA):
                        _join = j
                        break
                if _join < 0:
                    matched = False
                    break  # no consonant found in host, skip
                # Block the join if an independent vowel sits between the
                # consonant and the suffix (e.g. भए + को -> भएको: ए between
                # भ and को means no schwa deletion on भ).
                _suf_start = len(_host)
                _blocked = False
                for _k in range(_join + 1, _suf_start):
                    if _host[_k] not in _MATRA_NASAL_SET:
                        _blocked = True
                        break
                if _blocked:
                    matched = False
                    break  # skip this suffix, don't record join
                join_idxs.add(_join)
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
                _, _host_retain, _ = _u5(_host, _auto_tag(_host))
                _host_bases = sum(1 for c in _host if _is_consonant_base(c) or c in INDEP_VOWEL)
                # Host-final base consonant (skip matras / nasals / virama).
                _host_final = None
                for _c in reversed(_host):
                    if _is_consonant_base(_c):
                        _host_final = _c
                        break
                # At a compound join the host's final inherent /a/ is deleted UNLESS
                # the host-final consonant is a liquid/glide, which surfaces as a
                # syllable PEAK and is retained (नेपाल->Nepa:l, घर->ghar before a
                # suffix). This generalizes R7: a polysyllabic host drops its final
                # schwa at the boundary regardless of its standalone U5 decision
                # (so समाज->sama:j, सिमेन्ट->simenT, पार्क->pa:rk lose their final
                # /a/ before वाला, while नेपाल/घर keep the liquid peak). Monosyllabic
                # hosts (उस/कस/...) are handled by the curated list, not here.
                # At a compound join the host's final inherent /a/ is deleted when
                # EITHER (a) the host itself deletes its final schwa standalone
                # (U5 retain=False: HALANTA_FINAL नेपाल/घर, C6 कलम/करण), OR
                # (b) the host-final consonant is a NON-liquid stop/affricate. A
                # non-liquid stem-final drops its /a/ before a suffix (पार्क->pa:rk,
                # समाज->sama:j, सिमेन्ट->simenT all lose the final /a/ before वाला),
                # while a liquid/glide final surfaces as a syllable PEAK and is
                # retained (यस->yas before a suffix). Monosyllabic hosts (उस/कस/...)
                # are handled by the curated list, not here.
                _drops = (_host_bases > 1 or _host.endswith(VI_RAMA)) and \
                    ((not _host_retain) or
                     (_host_final is not None and _host_final not in _LIQUID_GLIDE))
                host_drops[_join] = _drops
                _remaining = _host
                matched = True
                break
        if not matched:
            # Check number-compound suffixes (e.g. चालीस, हत्तर). These also
            # trigger R7 join schwa deletion at the prefix boundary, but the
            # prefix ALWAYS drops its final schwa (unlike postpositions which
            # have complex retention rules). Number suffixes do NOT set
            # is_postposition — number words use C6 default DELETE.
            for suf in sorted(_NUM_COMPOUND_SUFFIXES, key=len, reverse=True):
                if _remaining.endswith(suf) and len(_remaining) > len(suf):
                    _host = _remaining[:len(_remaining) - len(suf)]
                    _join = -1
                    for j in range(len(_host) - 1, -1, -1):
                        if _is_consonant_base(_host[j]) and \
                                (j + 1 >= len(_host) or _host[j + 1] != VI_RAMA):
                            _join = j
                            break
                    if _join < 0:
                        continue  # no consonant in host, try next suffix
                    _suf_start = len(_host)
                    _blocked = False
                    for _k in range(_join + 1, _suf_start):
                        if _host[_k] not in _MATRA_NASAL_SET:
                            _blocked = True
                            break
                    if _blocked:
                        continue  # try next suffix
                    join_idxs.add(_join)
                    host_drops[_join] = True  # prefix always drops in number compounds
                    _remaining = _host
                    matched = True
                    break
        if not matched:
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
            if cp == "\u0935":  # Devanagari 'व'
                prev_is_virama = (i > 0 and cps[i - 1] == VI_RAMA)
                is_initial = (i == 0)
                is_foreign = tags.get("foreign", False) if tags else False
                if prev_is_virama:
                    out.append("v")  # Rule 1: Cluster protection (स्वाद, विश्वास -> v)
                elif is_initial and not is_foreign:
                    out.append("b")  # Rule 2: Native Tadbhava initial onset shift (वन, विकास -> b)
                else:
                    out.append("v")  # Rule 3: Foreign loans (वकिल, वकालत -> v) & medial glides
            elif cp == "\u092d":  # Devanagari 'भ' (bh)
                # R7.1: post-vocalic de-aspiration in rapid speech (e.g. अनुभव -> anubab, सुलभ -> sulab)
                is_post_vocalic = (i > 0 and out and out[-1] in _inv.VOWELS)
                if is_post_vocalic:
                    out.append("b")
                else:
                    out.append("bh")
            else:
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
            if nxt is not None and nxt in INDEP_VOWEL:
                # Independent vowels अ (U+0905), आ (U+0906), इ (U+0907),
                # ई (U+0908), उ (U+0909), ऊ (U+090A), ऋ (U+090B) REPLACE
                # the consonant's inherent /a/ (e.g. भ+इ+न् -> bhin; न+अ -> n).
                # ए/ऐ/ओ/ औ (U+090F/U+0910/U+0913/U+0914) form separate
                # syllables (e.g. भ+ए+को -> bhaeko).
                if nxt in ("\u0905", "\u0906", "\u0907", "\u0908",
                           "\u0909", "\u090a", "\u090b"):
                    i += 1
                    continue
            # live consonant with inherent /a/ UNLESS it is the FINAL consonant
            # and U5 decided DELETE (C6/C0/C1-Lneg), OR it is the host-final
            # consonant at a compound join (R7), OR it forms a medial cluster
            # with the following consonant (R7-general: fricative+stop etc.).
            is_final = (i == n - 1)
            medial = False
            _ohala_boundary = min(join_idxs) if join_idxs else -1
            if not (is_final and not retain) and i not in join_idxs:
                # Ohala internal schwa deletion: a live consonant followed by a
                # liquid/glide that begins a new syllable drops its /a/.
                medial = _ohala_internal_schwa(cps, i, _ohala_boundary)
            if (is_final and not retain and not is_postposition) or \
                    (i in join_idxs and host_drops.get(i, False)) or medial:
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
            # If no following consonant, default to 'N' (dental [n]; word-final ं).
            nxt_cons = _next_consonant_token(cps, i)
            nasal = _ANUSVARA_NASAL.get(nxt_cons, "N")
            out.append(nasal)
            i += 1
            continue

        if cp == VISARGA:
            # R2.4: Visarga is SILENT when followed by a consonant (e.g. दुःख -> dukha)
            nxt_c = cps[i + 1] if i + 1 < n else None
            if nxt_c is not None and _is_consonant_base(nxt_c):
                pass  # silent before consonant (Sanskrit retention)
            else:
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
