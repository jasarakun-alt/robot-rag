"""TDD: /search in /health API. Store prednastavimo z lokalnim embedderjem (brez omrežja)."""
from __future__ import annotations

import hashlib
import math
import re

from fastapi.testclient import TestClient

import retrieval_app
from store import VectorStore, chunk_markdown

MANUAL = """# Priročnik

Uvodni del.

## Ultrazvočni senzor

Ultrazvočni senzor meri razdaljo do ovire z odbojem zvoka.

## Baterije

Baterijo polnimo z ustreznim polnilnikom in pazimo na pravilno polariteto.
"""


def _local_embed(texts, input_type=None):
    rx = re.compile(r"\w+", re.UNICODE)
    dim = 256
    out = []
    for t in texts:
        v = [0.0] * dim
        for tok in rx.findall(t.lower()):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            v[h % dim] += 1.0 if (h >> 8) % 2 == 0 else -1.0
        n = math.sqrt(sum(x * x for x in v))
        out.append([x / n for x in v] if n else v)
    return out


def _client():
    store = VectorStore(_local_embed)
    store.index(chunk_markdown(MANUAL))
    retrieval_app.app.state.store = store  # prepreči klic na embedding storitev
    return TestClient(retrieval_app.app)


def test_health_reports_chunks():
    r = _client().get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["chunks"] == 3


def test_search_returns_relevant_chunk_with_source():
    r = _client().post("/search", json={"query": "ultrazvočni senzor razdalja", "k": 2})
    assert r.status_code == 200
    body = r.json()
    assert len(body["results"]) == 2
    top = body["results"][0]
    assert top["title"] == "Ultrazvočni senzor"
    assert "razdaljo" in top["text"]
    assert "score" in top and "source" in top


def test_search_default_k():
    r = _client().post("/search", json={"query": "baterija polnjenje"})
    assert r.status_code == 200
    assert len(r.json()["results"]) >= 1
