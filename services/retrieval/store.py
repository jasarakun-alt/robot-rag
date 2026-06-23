"""Chunking priročnika in vektorski indeks z kosinusnim iskanjem.

Indeks je v pomnilniku (priročnik je majhen). Embeddinge dobimo prek vbrizgane
funkcije embed_fn(texts, input_type) -> List[List[float]] (vektorji so že
L2-normalizirani, zato je kosinusna podobnost kar skalarni produkt).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np

_H1 = re.compile(r"^#\s+(.*)$")
_H2 = re.compile(r"^##\s+(.*)$")


@dataclass
class Chunk:
    id: int
    title: str
    text: str
    source: str = "prirocnik.md"


@dataclass
class SearchResult:
    chunk: Chunk
    score: float


def chunk_markdown(md: str, source: str = "prirocnik.md") -> List[Chunk]:
    """Razdeli markdown na chunke: uvodni del (H1) + vsak razdelek (H2)."""
    sections: List[tuple] = []
    title: Optional[str] = None
    buf: List[str] = []

    def push(t: Optional[str], lines: List[str]) -> None:
        if t is None:
            return
        body = "\n".join(lines).strip()
        if body:
            sections.append((t.strip(), body))

    for line in md.splitlines():
        m2 = _H2.match(line)
        if m2:
            push(title, buf)
            title, buf = m2.group(1), []
            continue
        m1 = _H1.match(line)
        if m1 and title is None and not sections:
            title, buf = m1.group(1), []
            continue
        if title is not None:
            buf.append(line)
    push(title, buf)

    return [Chunk(i, t, b, source) for i, (t, b) in enumerate(sections)]


EmbedFn = Callable[[List[str], Optional[str]], List[List[float]]]


class VectorStore:
    def __init__(self, embed_fn: EmbedFn):
        self.embed_fn = embed_fn
        self.chunks: List[Chunk] = []
        self._matrix: Optional[np.ndarray] = None

    def index(self, chunks: List[Chunk]) -> None:
        self.chunks = list(chunks)
        if not self.chunks:
            self._matrix = np.zeros((0, 0))
            return
        vectors = self.embed_fn([c.text for c in self.chunks], "passage")
        self._matrix = np.asarray(vectors, dtype=float)

    def search(self, query: str, k: int = 3) -> List[SearchResult]:
        if not self.chunks or self._matrix is None or self._matrix.size == 0:
            return []
        qv = np.asarray(self.embed_fn([query], "query")[0], dtype=float)
        # Vhodi so vedno končni in L2-normalizirani; numpy 2.0 + Apple Accelerate
        # tu včasih sproži lažna FP opozorila, zato jih za to operacijo utišamo.
        with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
            sims = self._matrix @ qv
        k = max(0, min(k, len(self.chunks)))
        top = np.argsort(-sims)[:k]
        return [SearchResult(self.chunks[int(i)], float(sims[int(i)])) for i in top]
