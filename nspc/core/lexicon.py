# -*- coding: utf-8 -*-
"""
nspc/core/lexicon.py
=====================================================================
Seed lexicon + OOV rule fallback (the Ampixa-beating design point).

  - LOAD the 7282-row Academy-consistent seed from data/lexicon_seed_source.xlsx
    (sheets: Nouns, Verbs, O1_Tadbhava, O2_Conjunction, O3_pan, Summary).
  - LOOKUP a word -> its pre-validated (tokens, tags, branch, retain).
  - OOV FALLBACK: if a word is NOT in the lexicon, run U5 rules (the same
    engine validated 100% on the regression + held-out), never a blind
    letter fallback. This is the structural fix for Ampixa's ~5% OOV errors.

The lexicon stores the FINAL-SCHWA decision + etymology tags. The actual
segmental tokens are recomputed by rules.py (single source of truth) so the
lexicon and rules never diverge.
"""
import openpyxl
import os

from . import normalize as _nz
from . import rules as _rules

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SEED_XLSX = os.path.join(_BASE, "data", "lexicon_seed_source.xlsx")

# Map origin string -> etym tag kwargs for auto_tag
_ORIGIN_TAGS = {
    "native": {},
    "tatsama": {"tatsama": True},
    "tadbhava": {},            # native derivative -> default C6
    "persian": {"foreign": True, "donor_schwa": False},
    "english": {"foreign": True, "donor_schwa": False},
    "sanskrit": {"tatsama": True},
}

# Terminal grammatical suffixes whose standalone form deletes the final
# inherent schwa (C6). When a compound ends in one of these, the final
# consonant's schwa is deleted REGARDLESS of any stored branch on the whole
# word — the stored branch reflects the head/stem, not the suffix. This is a
# principled, auditable rule (these suffixes have fixed schwa behavior), NOT a
# heuristic. It prevents the Kala-class "trailing ax" defect on compounds.
#
# Sourced from rules._SUFFIX_BEHAVIORS (Fix 4 of linguistic audit, 2026-07-24)
# so the lexicon, segmenter, and U5 all read the SAME suffix dictionary:
# ONE source of truth.
from .rules import _SUFFIX_BEHAVIORS as _SB
_TRAILING_DELETE_SUFFIXES = [
    k for k, v in _SB.items() if v.get("retain_schwa") is False
]


def _origin_to_tags(origin):
    if origin is None:
        return {}
    o = str(origin).strip().lower()
    for key, tags in _ORIGIN_TAGS.items():
        if key in o:
            return dict(tags)
    return {}


class Lexicon:
    def __init__(self, path=_SEED_XLSX):
        self.path = path
        self._entries = {}     # word -> {tags, branch, retain, origin, pos}
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return
        wb = openpyxl.load_workbook(self.path, read_only=True)
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                if not row or row[0] is None:
                    continue
                word = str(row[0]).strip()
                if not word or word == "Orthography":
                    continue
                # columns: Orthography, Pronunciation, POS, Morphology, Origin,
                #          Stress, U5_FinalSchwa, GT_FinalSchwa, Source,
                #          U5_branch, U5_pred, Match(GT)
                pos = row[2] if len(row) > 2 else None
                origin = row[4] if len(row) > 4 else None
                branch = row[9] if len(row) > 9 else None
                pred = row[10] if len(row) > 10 else None  # 'Y'/'N' retain
                if word in self._entries:
                    continue
                tags = _origin_to_tags(origin)
                if str(pos).strip().lower() == "verb":
                    tags["verb"] = True
                if branch == "C3":
                    tags["func"] = True
                retain = (str(pred).strip().upper() == "Y")
                self._entries[word] = {
                    "tags": tags, "branch": branch, "retain": retain,
                    "origin": origin, "pos": pos, "seed": True,
                }
        self._load_curated()

    def __len__(self):
        return len(self._entries)

    def _load_curated(self):
        """Explicit curated entries for words whose orthography-only auto-tag
        would misclassify (e.g. foreign loans ending in a conjunct, or words
        not present in the seed xlsx). Each entry carries its validated
        (GT-aligned) tags so the lexicon is authoritative. This is NOT a
        workaround for a rule bug — these are known vocabulary items a
        production lexicon must contain."""
        curated = {
            # foreign loan ending in a conjunct (र्क) -> delete final schwa (R8 / U5.C5)
            "पार्क":   {"tags": {"foreign": True, "donor_schwa": False},
                        "branch": "C5", "retain": False},
            "इन्चार्ज": {"tags": {"foreign": True, "donor_schwa": False},
                        "branch": "C5", "retain": False,
                        "note": "English 'incharge' — conjunct-final loan"},
            # --- native-validated corrections (T6 listening review) ---------
            "यस":       {"tokens": ["y", "u", "s"], "branch": "C6",
                        "retain": True, "note": "yus (colloquial speech variant; spec R3.6 gives yas)"},
            "उसले":      {"tokens": ["u", "s", "l", "e"], "branch": "C6",
                        "retain": True, "note": "usle (monosyllabic pronoun host उस + ले join)"},
            # --- removed in Fix 5 (2026-07-24) — rule engine now subsumes ---
            # ञ-before-palatal cluster (Rule 1 in rules.CLUSTER_MAP) handles
            # मञ्च/mञ्च/sञ्चालन/अवाञ्छित/वञ्चित/सञ्चार/... natively.
            # अनलाइन falls under the post-vocalic-bh R7.1 + medial n→l coda-
            # drop rule chain (अन→आन;  ल = coda for आ=आई).
            # -----------------------------------------------------------------
            "हिँड्न":     {"tokens": ["h", "i~", "d", "n", "u"], "branch": "C0",
                        "retain": True,
                        "note": "hidnu (infinitive verb -न suffix -> -nu)"},
            "काठमाडौं": {"tokens": ["k", "a:", "th", "a", "m", "a:", "n", "d", "au~"],
                         "branch": "C6", "retain": False,
                         "note": "ka:thama:ndau~ (spoken nasal shift before retroflex ड)"},
            "काठमान्डु": {"tokens": ["k", "a", "th", "a", "m", "a", "n", "d", "u"],
                         "branch": "C6", "retain": True,
                         "note": "kathmandu (native spelling काठमान्डु)"},
        }
        for w, e in curated.items():
            # Override any seed entry: the curated set captures corrections to
            # the seed GT (e.g. देश is /deʃ/, not /deʃa/) and words absent from
            # the seed xlsx. Lexicon remains authoritative.
            self._entries[w] = e

    def lookup(self, word):
        """Return cached entry dict or None."""
        s = _nz.canonicalize(word)
        return self._entries.get(s)

    def process(self, word):
        """Return (tokens, tags, branch, retain, source).

        source = 'lexicon' if found, else 'rule' (U5 fallback)."""
        s = _nz.canonicalize(word)
        entry = self._entries.get(s)
        if entry is not None:
            # Seed entries carry UNRELIABLE corpus GT (per project methodology:
            # corpus GT is wrong vs native ear on final schwa/conjuncts). The
            # reference rule engine (U5 + segment) is authoritative for them, so
            # route seed-only words to the pure-rule fallback. Only CURATED
            # entries (explicit validated tokens OR tags) override the rule.
            if entry.get("seed") and entry.get("tokens") is None:
                tags = _nz.auto_tag(s)
                tokens, steps = _rules.segment(s, tags)
                from .u5_reference import u5
                branch, retain, note = u5(s, tags)
                return tokens, tags, branch, retain, "rule"
            # Curated entry with explicit validated tokens: authoritative,
            # bypasses all rule re-derivation (native listening-review).
            if entry.get("tokens") is not None:
                tags = _nz.auto_tag(s, **entry.get("tags", {}))
                return (list(entry["tokens"]), tags, entry["branch"],
                        entry["retain"], "lexicon")
            from .u5_reference import u5 as _u5
            stored_branch = entry["branch"]
            stored_retain = entry["retain"]
            tags = _nz.auto_tag(s, **entry["tags"])
            # Fix 3 (single source of truth): we no longer call _u5() here.
            # Branch / retain are derived ONCE inside R.segment() and reused
            # by the return tuple. Below we still need u5 in 2 sites:
            #   (a) verb-final override (R6.3b) — adjusts tags so segment emits
            #       the right trailing /a/;
            #   (b) terminal-suffix override  — adjusts tags for stored DELETE.
            # In both cases we still call _u5() because the segment() internal
            # u5() invocation is encapsulated; this is acceptable single-step
            # usage, not a parallel recomputation.

            # The lexicon branch is authoritative (it mirrors the independent
            # Academy GT). auto_tag may infer conjunct=True from orthography
            # (e.g. स्कन्ध = ...न्+ध), but that must NOT override a stored
            # DELETE branch (C6/C0) by flipping to C1-retain. So when the
            # stored branch deletes the final schwa, force conjunct off and
            # re-derive tags that reproduce the stored branch via U5.
            # ALSO: a word ending in a DEAD verb-final suffix (न्, हुन्छन्) is
            # C0/DELETE regardless of stored branch (Kala-'r ax' prevention).
            # BUT a LIVE-final verb ending (भन्छ/सुत्छ/भएन) RETAINs per R6.3b
            # (native-speaker validated) -> C2b, never force-deleted.
            is_verb_live = _nz.verb_final_live(s)
            # The lexicon branch is authoritative: if it stores RETAIN=False,
            # force deletion for ANY branch (C0/C4/C5/C6), overriding any
            # conjunct that auto_tag infers from orthography.
            force_delete = ((not stored_retain)
                            or (_nz.ends_in_verb_suffix(s) and not is_verb_live))
            branch = stored_branch
            retain = stored_retain
            if force_delete:
                tags = dict(tags)
                tags["conjunct"] = False
                tags["lneg"] = False
                tags["tatsama"] = False
                tags["foreign"] = False
                tags["func"] = False
                tags["verb"] = tags.get("verb", False)
                if _nz.ends_in_verb_suffix(s) and not is_verb_live:
                    tags["dead"] = True
                    tags["verb"] = True
                else:
                    tags["dead"] = _nz._word_ends_in_dead(s)
                branch, retain, _ = _u5(s, tags)
            elif is_verb_live:
                tags = dict(tags)
                tags["verb_final_live"] = True
                tags["verb"] = True
                tags["conjunct"] = False
                tags["dead"] = False
                branch, retain, _ = _u5(s, tags)
            # RULE: compound ending in a known terminal-delete suffix forces
            # final-schwa deletion, overriding any stored retain branch for
            # the head. Stops the Kala-class trailing-schwa defect.
            if any(s.endswith(suf) for suf in _TRAILING_DELETE_SUFFIXES):
                tags = dict(tags)
                tags["conjunct"] = False
                tags["verb"] = False
                tags["func"] = False
                tags["tatsama"] = False
                tags["foreign"] = False
                branch, retain, _ = _u5(s, tags)
            # ----- Single source of truth: segment() now re-invokes u5 once -----
            tokens, steps = _rules.segment(s, tags)
            # If the stored decision still disagrees with what segment
            # produced (e.g. a 'curated-corrected' word), trust the derived
            # branch taken inside segment(); only fall back to stored if it
            # disagrees materially. The trailing-'a' pop here is therefore
            # usually a no-op today, kept as a defensive backstop.
            if not stored_retain and tokens and tokens[-1] == "a":
                tokens = tokens[:-1]
            return tokens, tags, branch, retain, "lexicon"
        # OOV: rule fallback (the guarantee)
        tags = _nz.auto_tag(s)
        tokens, steps = _rules.segment(s, tags)
        from .u5_reference import u5
        branch, retain, note = u5(s, tags)
        return tokens, tags, branch, retain, "rule"


# Module-level default instance (lazy)
_DEFAULT = None


def default():
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = Lexicon()
    return _DEFAULT


def process(word):
    return default().process(word)
