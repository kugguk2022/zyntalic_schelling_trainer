# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from zyntalic.translator import translate_text

app = FastAPI(title="Zyntalic API", version="0.2.0")

class TranslateRequest(BaseModel):
    text: str
    mirror_rate: float = 0.8
    engine: str = "core"  # "core"|"chiasmus"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/translate")
def translate(req: TranslateRequest):
    rows = translate_text(req.text, mirror_rate=req.mirror_rate, engine=req.engine)
    return {"rows": rows}
