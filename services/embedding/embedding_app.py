"""Embedding mikrostoritev (FastAPI). Pretvori besedilo v vektorje."""
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from embedder import get_embedder


class EmbedRequest(BaseModel):
    texts: List[str]
    input_type: Optional[str] = None  # "query" | "passage" | None


class EmbedResponse(BaseModel):
    vectors: List[List[float]]
    dim: int
    model: str


app = FastAPI(title="Embedding Service")
_embedder = get_embedder()


@app.get("/health")
def health():
    return {"status": "ok", "service": "embedding", "model": _embedder.name, "dim": _embedder.dim}


@app.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    vectors = _embedder.embed(req.texts, input_type=req.input_type)
    return EmbedResponse(vectors=vectors, dim=_embedder.dim, model=_embedder.name)
