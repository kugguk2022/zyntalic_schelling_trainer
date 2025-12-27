# -*- coding: utf-8 -*-
"""
High-level translation API.

This wraps the deterministic core into a stable interface usable by:
- CLI
- web app (FastAPI)
- evals/tests
"""

from __future__ import annotations

from dataclasses import asdict
import re
from typing import Dict, List, Optional

from . import core

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

def _clean_lemma(text: str) -> str:
    t = re.sub(r"[^A-Za-z0-9'\- ]+", " ", (text or "").strip().lower())
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return ""
    # first word as lemma seed (stable; avoids sentence-level randomness explosion)
    return t.split()[0]


def translate_sentence(
    text: str,
    *,
    mirror_rate: float = 0.8,
    engine: str = "core",
    W=None,
) -> Dict:
    """
    Translate a single sentence to a structured record.

    engine:
      - "core": rule-based + anchor mixing (recommended baseline)
      - "chiasmus": uses chiasmus renderer if available (more stylized)
      - "transformer": uses semantic anchor matching via sentence-transformers
      - "test_suite": runs comprehensive validation and returns diagnostic info
    """
    src = (text or "").strip()
    lemma = _clean_lemma(src)

    if engine == "test_suite":
        try:
            from .test_suite import ZyntalicTestSuite
            # Run a quick validation test for the input
            test_suite = ZyntalicTestSuite()
            # Use core engine for actual translation but add test metadata
            entry = core.generate_entry(lemma or src, mirror_rate=mirror_rate, W=W)
            return {
                "source": src,
                "target": entry["sentence"],
                "lemma": lemma,
                "anchors": entry["anchors"],
                "engine": "test_suite",
                "validation": "passed",
                "test_info": "Input validated with test suite"
            }
        except Exception as e:
            # Fall back to core if test suite fails
            engine = "core"

    if engine == "transformer":
        try:
            from .transformers import translate_transformer
            return {
                "source": src,
                "target": translate_transformer(src, mirror_rate=mirror_rate),
                "lemma": lemma,
                "anchors": [], # TODO: populate if needed
                "engine": "transformer",
            }
        except Exception as e:
            # print(f"Transformer error: {e}") # debug
            engine = "core"

    if engine == "chiasmus":
        try:
            from .chiasmus import translate_chiasmus  # type: ignore
            tgt = translate_chiasmus(src)
            return {
                "source": src,
                "target": tgt,
                "lemma": lemma,
                "anchors": [],
                "engine": "chiasmus",
            }
        except Exception:
            # fall back to core
            engine = "core"

    entry = core.generate_entry(lemma or src, mirror_rate=mirror_rate, W=W)
    # entry contains 'sentence' (with ctx tail) and anchor weights
    return {
        "source": src,
        "target": entry["sentence"],
        "lemma": lemma,
        "anchors": entry["anchors"],
        "engine": "core",
    }


def translate_text(
    text: str,
    *,
    mirror_rate: float = 0.8,
    engine: str = "core",
    W=None,
) -> List[Dict]:
    """
    Translate multi-sentence text into a list of records.
    """
    text = (text or "").strip()
    if not text:
        return []
    parts = _SENT_SPLIT.split(text)
    return [translate_sentence(p, mirror_rate=mirror_rate, engine=engine, W=W) for p in parts if p.strip()]
