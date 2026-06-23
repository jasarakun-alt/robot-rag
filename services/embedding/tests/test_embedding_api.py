"""TDD: testi za /embed API. Uporabljamo hash backend (brez torch)."""
from __future__ import annotations

import os

os.environ["EMBEDDING_BACKEND"] = "hash"
os.environ["EMBEDDING_DIM"] = "128"

from fastapi.testclient import TestClient  # noqa: E402

from embedding_app import app  # noqa: E402

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["dim"] == 128


def test_embed_returns_one_vector_per_text():
    r = client.post("/embed", json={"texts": ["robot", "senzor", "baterija"]})
    assert r.status_code == 200
    body = r.json()
    assert len(body["vectors"]) == 3
    assert body["dim"] == 128
    assert all(len(v) == 128 for v in body["vectors"])


def test_embed_empty_input():
    r = client.post("/embed", json={"texts": []})
    assert r.status_code == 200
    assert r.json()["vectors"] == []
