# -*- coding: utf-8 -*-
"""
nspc/core/adapters/__init__.py
=====================================================================
Adapters translate CANONICAL tokens (inventory.py) into the symbol set a
specific TTS trainer expects. The core NEVER emits engine-specific symbols;
adapters are the only place engine knowledge lives. This keeps the frontend
universal (engine-agnostic) per the kit design.
"""
from . import ipa, json, piper, matcha

__all__ = ["ipa", "json", "piper", "matcha"]
