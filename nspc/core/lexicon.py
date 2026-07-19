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
# Terminal suffixes whose final inherent /a/ is DELETED (silent). Verified by
# native speaker (2026-07): of the common postpositions, ONLY दार drops its
# final अ. बाट/तिर/सँग/हरू/मा/ले/सँगै/भरि/सम्म/पछि/अघि all RETAIN the final अ
# (e.g. करणबाट -> kəranbatə, देशतिर -> destirə, उससँग -> ussəgə).
# This list is the complete, audited set — do NOT add to it without native
# confirmation, since the prior 12-item list was wrong on 11 of 12.
_TRAILING_DELETE_SUFFIXES = [
    "दार",   # "having" (possessive) -> final अ silent
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
            # foreign loan ending in a conjunct (र्क) -> delete final schwa
            "पार्क":   {"tags": {"foreign": True, "donor_schwa": False},
                        "branch": "C5", "retain": False},
            # tatsama: विकास retains final schwa (vikās). (देश now covered by
            # U5 TATSAMA_DELETE; verb forms भन्छ/सुत्छ/हुन्छ/भएन by U5 C2b;
            # देशतिर/स्कन्ध/स्कुल by rule — all removed as redundant 2026-07-19.)
            "विकास":   {"tags": {"tatsama": True}, "branch": "C4", "retain": True},
            # --- native-validated corrections (T6 listening review) ---------
            # These override OOV-rule errors where Nepali deletes/keeps a
            # schwa that the orthography-only rule gets wrong. Each carries
            # its validated canonical tokens directly (authoritative).
            "यस":       {"tokens": ["y", "u", "s"], "branch": "C6",
                        "retain": True, "note": "yus (अ→u sound change)"},
            "उसले":     {"tokens": ["u", "s", "l", "e"], "branch": "C6",
                        "retain": True, "note": "usle (medial schwa deleted)"},
            "सरकार":    {"tokens": ["s", "a", "r", "k", "a", "r"], "branch": "C6",
                        "retain": True, "note": "sarkar (schwa after स deleted)"},
            "मञ्च":      {"tokens": ["m", "a", "n", "ch"], "branch": "C1",
                        "retain": False, "note": "manch (ञ silent; final अ dropped, speech variant)"},
            "अनलाइन":    {"tokens": ["a", "N", "l", "i", "N"], "branch": "C6",
                        "retain": True, "note": "unline (medial schwas deleted)"},
            "हिँड्न":     {"tokens": ["h", "i~", "d", "n", "u"], "branch": "C0",
                        "retain": True,
                        "note": "hidnu (infinitive न् retained; C0 exception)"},
            # काठमान्डु -> kathmandu (native spelling मान्डु; न्डु -> ndu)
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
        s = _nz.NFC(word)
        return self._entries.get(s)

    def process(self, word):
        """Return (tokens, tags, branch, retain, source).

        source = 'lexicon' if found, else 'rule' (U5 fallback)."""
        s = _nz.NFC(word)
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
            branch = stored_branch
            retain = stored_retain
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
            if force_delete:
                tags = dict(tags)
                # Neutralize every retention signal so U5 (and the segment()
                # recomputation) DELETE the final schwa. The lexicon's
                # RETAIN=False is authoritative; tatsama/foreign/conjunct flags
                # must not flip it back to retain.
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
                # override stored branch with R6.3b live-final verb retain
                tags = dict(tags)
                tags["verb_final_live"] = True
                tags["verb"] = True
                tags["conjunct"] = False
                tags["dead"] = False
                branch, retain, _ = _u5(s, tags)
            # RULE: a compound ending in a known terminal-delete suffix forces
            # final-schwa deletion on the absolute final consonant, overriding
            # any stored retain branch for the head. This is what stops the
            # Kala-class trailing-schwa defect (e.g. करणबाट -> ...ba T, not ...ba T a).
            if any(s.endswith(suf) for suf in _TRAILING_DELETE_SUFFIXES):
                tags = dict(tags)
                tags["conjunct"] = False
                tags["verb"] = False
                tags["func"] = False
                tags["tatsama"] = False
                tags["foreign"] = False
                branch, retain, _ = _u5(s, tags)
            tokens, steps = _rules.segment(s, tags)
            # The lexicon's stored retain decision is AUTHORITATIVE for the
            # produced tokens. Since C6 now defaults to RETAIN, an entry that
            # stores retain=False (tatsama देश->desh, foreign पार्क->park,
            # halanta घर->ghar) must have its final inherent 'a' stripped here
            # regardless of the segmenter's default. This realizes the stored
            # decision directly instead of relying on a flipped U5 branch.
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
