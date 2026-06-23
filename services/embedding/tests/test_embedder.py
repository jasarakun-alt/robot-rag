"""TDD: testi za embedder (logika vektorizacije). Pisani PRED implementacijo."""
from __future__ import annotations

import math

from embedder import HashingEmbedder


def cos(a, b):
    return sum(x * y for x, y in zip(a, b))


def test_dimension_matches():
    emb = HashingEmbedder(dim=128)
    vecs = emb.embed(["ultrazvočni senzor", "baterija"])
    assert len(vecs) == 2
    assert all(len(v) == 128 for v in vecs)
    assert emb.dim == 128


def test_deterministic_across_calls():
    emb = HashingEmbedder(dim=64)
    a = emb.embed(["robot vozi naprej"])[0]
    b = emb.embed(["robot vozi naprej"])[0]
    assert a == b


def test_vectors_are_unit_normalized():
    emb = HashingEmbedder(dim=64)
    v = emb.embed(["motor poganja kolesa"])[0]
    norm = math.sqrt(sum(x * x for x in v))
    assert abs(norm - 1.0) < 1e-6


def test_similar_texts_more_similar_than_unrelated():
    emb = HashingEmbedder(dim=512)
    q = emb.embed(["senzor meri razdaljo do ovire"])[0]
    related = emb.embed(["ultrazvočni senzor izmeri razdaljo do ovire"])[0]
    unrelated = emb.embed(["baterijo polnimo z ustreznim polnilnikom"])[0]
    assert cos(q, related) > cos(q, unrelated)


def test_empty_list_returns_empty():
    emb = HashingEmbedder(dim=32)
    assert emb.embed([]) == []


def test_empty_string_is_safe():
    emb = HashingEmbedder(dim=32)
    v = emb.embed([""])[0]
    assert len(v) == 32
    assert all(not math.isnan(x) for x in v)
