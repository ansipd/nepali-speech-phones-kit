# -*- coding: utf-8 -*-
"""piper.py — canonical -> Piper phoneme string.

Piper uses a phoneme_id_map (text -> id). We emit SPACE-SEPARATED canonical
tokens as the phoneme TEXT; the trainer's phoneme_id_map should be built from
INVENTORY.md (see examples/piper_dataset). This keeps tokens 1:1 with the
canonical set — no silent remapping.

We also expose build_phoneme_id_map() to generate the Piper config snippet.
"""
from .. import inventory as _inv

_SPACE = " "


def convert(tokens):
    """canonical tokens -> Piper phoneme text (space separated)."""
    return _SPACE.join(tokens)


def build_phoneme_id_map(pad="_", bos="^", eos="$"):
    """Generate Piper phoneme_id_map dict from the canonical inventory.

    The map is the SINGLE place that binds canonical tokens to Piper ids;
    it is generated, never hand-maintained, so it cannot drift from
    INVENTORY.md.
    """
    tokens = sorted(_inv.ALL_TOKENS)
    mapping = {pad: 0, bos: 1, eos: 2}
    for i, t in enumerate(tokens):
        mapping[t] = i + 3
    return mapping


def config_snippet():
    import json as _json
    m = build_phoneme_id_map()
    return "phoneme_id_map=" + _json.dumps(m, ensure_ascii=False)
