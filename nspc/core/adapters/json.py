# -*- coding: utf-8 -*-
"""json.py — canonical -> structured JSON for training pipelines.

Output shape (one word):
  {
    "text": "<devanagari>",
    "phones": "k a s",        # space-joined canonical tokens
    "tokens": ["k","a","s"],
    "oov": false,             # true if produced by rule fallback
    "branch": "C6",
    "trace": [ ... ]          # optional, for audit
  }
"""
import json as _json


def convert_word(result, include_trace=True):
    """result = output of nspc.core.lexicon.process + trace info.
    We accept the dict from a helper; keep it minimal here."""
    out = {
        "text": result.get("text", ""),
        "phones": " ".join(result.get("tokens", [])),
        "tokens": result.get("tokens", []),
        "oov": result.get("source", "rule") == "rule",
        "branch": result.get("branch"),
    }
    if include_trace and "trace" in result:
        out["trace"] = result["trace"]
    return out


def dumps(results, include_trace=True):
    items = [convert_word(r, include_trace) for r in results]
    return _json.dumps(items, ensure_ascii=False, indent=2)
