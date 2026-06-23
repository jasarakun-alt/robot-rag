"""Retrieval mikrostoritev (FastAPI). Hrani indeks priročnika in vrača top-k odlomkov."""
from __future__ import annotations

import os
from typing import List, Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from store import VectorStore, chunk_markdown


def remote_embed(texts: List[str], input_type: Optional[str] = None) -> List[List[float]]:
    """Embeddinge dobi od embedding mikrostoritve."""
    if not texts:
        return []
    url = os.environ.get("EMBEDDING_SERVICE_URL", "http://localhost:8001").rstrip("/") + "/embed"
    resp = httpx.post(url, json={"texts": texts, "input_type": input_type}, timeout=120)
    resp.raise_for_status()
    return resp.json()["vectors"]


def _manual_path() -> str:
    env = os.environ.get("MANUAL_PATH")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "..", "data", "prirocnik.md")


def init_store(embed_fn, path: str) -> VectorStore:
    with open(path, encoding="utf-8") as f:
        md = f.read()
    store = VectorStore(embed_fn)
    store.index(chunk_markdown(md, source=os.path.basename(path)))
    return store


app = FastAPI(title="Retrieval Service")
app.state.store = None


def get_store() -> VectorStore:
    if app.state.store is None:
        app.state.store = init_store(remote_embed, _manual_path())
    return app.state.store


class SearchRequest(BaseModel):
    query: str
    k: int = int(os.environ.get("TOP_K", "3"))


@app.get("/health")
def health():
    store = get_store()
    return {"status": "ok", "service": "retrieval", "chunks": len(store.chunks)}


@app.post("/search")
def search(req: SearchRequest):
    store = get_store()
    results = store.search(req.query, k=req.k)
    return {
        "query": req.query,
        "results": [
            {
                "title": r.chunk.title,
                "text": r.chunk.text,
                "score": r.score,
                "source": r.chunk.source,
            }
            for r in results
        ],
    }
