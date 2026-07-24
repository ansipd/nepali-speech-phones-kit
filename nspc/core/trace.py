# -*- coding: utf-8 -*-
"""
nspc/core/trace.py
=====================================================================
Deterministic, human-readable trace for SPEC §12 ("why did this word sound
like that?"). Wraps g2p + normalize so any output is fully auditable.

Output of trace_word is a dict: {
  surface, nfc, tags, branch, retain, tokens, ipa, steps[]
}
"""
from . import normalize as _nz
from . import rules as _rules
from . import inventory as _inv


def trace_word(word, **etym):
    s = _nz.NFC(word)
    facts = _nz.analyze(s)
    tags = _nz.auto_tag(s, **etym)
    tokens, steps = _rules.segment(s, tags)
    from .u5_reference import u5
    branch, retain, note = u5(s, tags)
    ipa = _inv.to_ipa(tokens)
    return {
        "surface": word,
        "nfc": s,
        "codepoints": facts["codepoints"],
        "tags": tags,
        "branch": branch,
        "retain": retain,
        "note": note,
        "tokens": tokens,
        "ipa": ipa,
        "steps": steps,
    }


def format_trace(tr):
    lines = ["=== " + tr["surface"] + " ==="]
    lines.append("NFC      : " + tr["nfc"])
    lines.append("codepoints: " + " ".join(tr["codepoints"]))
    lines.append("tags     : " + str({k: v for k, v in tr["tags"].items()
                                      if not k.startswith("_")}))
    lines.append("branch   : U5." + tr["branch"] + " (" +
                 ("RETAIN" if tr["retain"] else "DELETE") + ")")
    lines.append("tokens   : " + " ".join(tr["tokens"]))
    lines.append("IPA      : /" + tr["ipa"] + "/")
    return "\n".join(lines)
