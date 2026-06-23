"""TDD: /generate (+model/language), /translate, /models. Ollama klic je mockiran."""
from __future__ import annotations

from fastapi.testclient import TestClient

import llm_app
import ollama_client


def test_generate_uses_context_only_prompt(monkeypatch):
    captured = {}

    def fake_generate(messages, **kwargs):
        captured["messages"] = messages
        return "Ultrazvočni senzor meri razdaljo z zvokom."

    monkeypatch.setattr(ollama_client, "generate", fake_generate)
    client = TestClient(llm_app.app)
    r = client.post(
        "/generate",
        json={
            "question": "Kaj je ultrazvočni senzor?",
            "contexts": [{"title": "Ultrazvočni senzor", "text": "meri razdaljo do ovire"}],
        },
    )
    assert r.status_code == 200
    assert "razdaljo" in r.json()["answer"]
    system = next(m["content"] for m in captured["messages"] if m["role"] == "system")
    assert "IZKLJUČNO" in system


def test_generate_passes_model_and_language(monkeypatch):
    captured = {}

    def fake_generate(messages, **kwargs):
        captured["messages"] = messages
        captured["model"] = kwargs.get("model")
        return "answer"

    monkeypatch.setattr(ollama_client, "generate", fake_generate)
    client = TestClient(llm_app.app)
    r = client.post(
        "/generate",
        json={"question": "q", "contexts": [], "model": "gemma3:27b", "language": "angleščina"},
    )
    assert r.status_code == 200
    assert r.json()["model"] == "gemma3:27b"
    assert captured["model"] == "gemma3:27b"
    system = next(m["content"] for m in captured["messages"] if m["role"] == "system")
    assert "angleščina" in system


def test_translate_endpoint(monkeypatch):
    monkeypatch.setattr(ollama_client, "generate", lambda messages, **kw: "translated text")
    client = TestClient(llm_app.app)
    r = client.post("/translate", json={"text": "Pozdravljen", "target_language": "angleščina"})
    assert r.status_code == 200
    assert r.json()["text"] == "translated text"


def test_models_endpoint(monkeypatch):
    monkeypatch.setattr(
        ollama_client, "list_models", lambda: [{"name": "qwen2.5:14b", "parameter_size": "14.8B", "size": 9000}]
    )
    client = TestClient(llm_app.app)
    r = client.get("/models")
    assert r.status_code == 200
    assert r.json()["models"][0]["name"] == "qwen2.5:14b"


def test_health_does_not_require_ollama():
    client = TestClient(llm_app.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
