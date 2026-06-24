"""Chunking priročnika in kosinusno iskanje."""
from __future__ import annotations

import hashlib
import math
import os
import re

from store import Chunk, VectorStore, chunk_markdown

SAMPLE = """# Glavni naslov

Uvodni odstavek pred poglavji.

## Prvo poglavje

Vsebina ena o senzorjih.

## Drugo poglavje

Vsebina dve o baterijah.
"""


def test_chunk_includes_preamble_and_sections():
    titles = [c.title for c in chunk_markdown(SAMPLE)]
    assert titles == ["Glavni naslov", "Prvo poglavje", "Drugo poglavje"]


def test_chunk_text_is_section_local():
    prvo = [c for c in chunk_markdown(SAMPLE) if c.title == "Prvo poglavje"][0]
    assert "Vsebina ena" in prvo.text
    assert "Vsebina dve" not in prvo.text


def test_no_empty_chunks():
    chunks = chunk_markdown(SAMPLE)
    assert all(c.text.strip() for c in chunks)
    assert all(c.title.strip() for c in chunks)


def test_ids_are_sequential():
    assert [c.id for c in chunk_markdown(SAMPLE)] == [0, 1, 2]


# ---------- iskanje z injiciranimi (kontroliranimi) vektorji ----------

def _fake_embed(texts, input_type=None):
    table = {
        "alfa vsebina": [1.0, 0.0, 0.0],
        "beta vsebina": [0.0, 1.0, 0.0],
        "gama vsebina": [0.0, 0.0, 1.0],
        "iščem beta": [0.05, 0.99, 0.0],
    }
    return [table[t] for t in texts]


def test_search_ranks_relevant_first():
    chunks = [
        Chunk(0, "A", "alfa vsebina", "s"),
        Chunk(1, "B", "beta vsebina", "s"),
        Chunk(2, "C", "gama vsebina", "s"),
    ]
    store = VectorStore(_fake_embed)
    store.index(chunks)
    res = store.search("iščem beta", k=2)
    assert len(res) == 2
    assert res[0].chunk.title == "B"
    assert res[0].score > res[1].score


def test_search_k_truncates():
    chunks = [Chunk(i, str(i), f"{w} vsebina", "s") for i, w in enumerate(["alfa", "beta", "gama"])]
    store = VectorStore(_fake_embed)
    store.index(chunks)
    assert len(store.search("iščem beta", k=1)) == 1


def test_search_empty_store_returns_empty():
    store = VectorStore(_fake_embed)
    store.index([])
    assert store.search("karkoli", k=3) == []


# ---------- realističen test nad pravim priročnikom (lokalni hashing) ----------

def _hash_embed(texts, input_type=None):
    rx = re.compile(r"\w+", re.UNICODE)
    dim = 512
    out = []
    for t in texts:
        v = [0.0] * dim
        for tok in rx.findall(t.lower()):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            v[h % dim] += 1.0 if (h >> 8) % 2 == 0 else -1.0
        n = math.sqrt(sum(x * x for x in v))
        out.append([x / n for x in v] if n else v)
    return out


def test_real_manual_retrieves_ultrasonic():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "prirocnik.md")
    md = open(path, encoding="utf-8").read()
    chunks = chunk_markdown(md)
    assert len(chunks) >= 10
    store = VectorStore(_hash_embed)
    store.index(chunks)
    res = store.search("Kaj je ultrazvočni senzor in kako meri razdaljo?", k=3)
    assert any("ultrazvočni" in r.chunk.title.lower() for r in res)
