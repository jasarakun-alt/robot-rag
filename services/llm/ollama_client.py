"""Tanek klient za Ollama (/api/chat). Pure funkcije so ločene zaradi testabilnosti."""
from __future__ import annotations

import os
from typing import Dict, List

import httpx


def build_payload(messages: List[Dict], model: str, temperature: float, stream: bool = False) -> Dict:
    return {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {"temperature": temperature},
    }


def parse_chat_response(data: Dict) -> str:
    try:
        content = data["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Nepričakovan odgovor Ollame: {data!r}") from exc
    return content.strip()


def parse_tags(data: Dict) -> List[Dict]:
    """Iz odgovora /api/tags izlušči seznam modelov."""
    out = []
    for m in data.get("models", []) or []:
        details = m.get("details", {}) or {}
        out.append(
            {
                "name": m.get("name"),
                "size": m.get("size"),
                "parameter_size": details.get("parameter_size"),
                "family": details.get("family"),
            }
        )
    return out


def list_models(base_url=None, timeout=30) -> List[Dict]:
    base = (base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
    resp = httpx.get(base + "/api/tags", timeout=timeout)
    resp.raise_for_status()
    return parse_tags(resp.json())


def generate(messages, model=None, temperature=None, base_url=None, timeout=300):
    base = (base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
    model = model or os.environ.get("LLM_MODEL", "qwen2.5:14b")
    if temperature is None:
        temperature = float(os.environ.get("LLM_TEMPERATURE", "0.1"))
    payload = build_payload(messages, model, temperature)
    resp = httpx.post(base + "/api/chat", json=payload, timeout=timeout)
    resp.raise_for_status()
    return parse_chat_response(resp.json())
