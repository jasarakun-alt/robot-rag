"""Vektorizacija besedila.

Dva zaledja (backend):
  * HashingEmbedder        – deterministični, brez odvisnosti (offline/dev/testi)
  * SentenceTransformerEmbedder – realni večjezični embeddingi (produkcija)

get_embedder() izbere zaledje glede na okoljsko spremenljivko EMBEDDING_BACKEND.
"""
from __future__ import annotations

import hashlib
import math
import os
import re
import sys
from typing import List, Optional

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _l2_normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


class HashingEmbedder:
    """Bag-of-words s predznačenim zgoščevanjem (signed hashing) v fiksno dimenzijo.

    Besede z istim zapisom padejo v isti predalček z istim predznakom, zato
    imata besedili s skupnimi besedami pozitivno kosinusno podobnost, nepovezani
    besedili pa skoraj ničelno. Dovolj za teste in offline delovanje.
    """

    name = "hash"

    def __init__(self, dim: int = 256):
        self.dim = dim

    def _vectorize(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for token in _TOKEN_RE.findall(text.lower()):
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign
        return _l2_normalize(vec)

    def embed(self, texts: List[str], input_type: Optional[str] = None) -> List[List[float]]:
        return [self._vectorize(t) for t in texts]


class SentenceTransformerEmbedder:
    """Realni večjezični embeddingi prek sentence-transformers."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.name = model_name
        self.dim = int(self.model.get_sentence_embedding_dimension())

    def _with_prefix(self, texts: List[str], input_type: Optional[str]) -> List[str]:
        # Modeli družine e5 pričakujejo predpono "query: " / "passage: ".
        if "e5" in self.name.lower() and input_type in ("query", "passage"):
            return [f"{input_type}: {t}" for t in texts]
        return list(texts)

    def embed(self, texts: List[str], input_type: Optional[str] = None) -> List[List[float]]:
        if not texts:
            return []
        prefixed = self._with_prefix(texts, input_type)
        vectors = self.model.encode(prefixed, normalize_embeddings=True)
        return [list(map(float, v)) for v in vectors]


def get_embedder():
    backend = os.environ.get("EMBEDDING_BACKEND", "sentence-transformers").lower()
    if backend in ("hash", "hashing", "dev"):
        return HashingEmbedder(dim=int(os.environ.get("EMBEDDING_DIM", "256")))

    model_name = os.environ.get("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    try:
        return SentenceTransformerEmbedder(model_name)
    except Exception as exc:  # pragma: no cover - varni fallback ob manjkajočem torch
        print(
            f"[embedding] sentence-transformers ni na voljo ({exc}); uporabljam hash backend.",
            file=sys.stderr,
        )
        return HashingEmbedder(dim=int(os.environ.get("EMBEDDING_DIM", "256")))
