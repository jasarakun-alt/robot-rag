"""TDD: gateway orkestracija /ask (+model/jezik/pivot), /models, /faq, /health."""
from __future__ import annotations

from fastapi.testclient import TestClient

import gateway_app


def test_ask_orchestrates_and_returns_sources(monkeypatch):
    fake_contexts = [
        {"title": "Ultrazvočni senzor", "text": "meri razdaljo do ovire", "score": 0.9, "source": "prirocnik.md"}
    ]

    def fake_retrieve(question, k):
        assert question
        return fake_contexts

    def fake_generate(question, contexts, model=None, language=None):
        assert contexts == fake_contexts
        return {"answer": "Ultrazvočni senzor meri razdaljo z zvokom.", "model": "test-model"}

    monkeypatch.setattr(gateway_app, "retrieve", fake_retrieve)
    monkeypatch.setattr(gateway_app, "generate", fake_generate)

    client = TestClient(gateway_app.app)
    r = client.post("/ask", json={"question": "Kaj je ultrazvočni senzor?"})
    assert r.status_code == 200
    body = r.json()
    assert "razdaljo" in body["answer"]
    assert body["question"] == "Kaj je ultrazvočni senzor?"
    assert body["sources"] == fake_contexts
    assert "elapsed_ms" in body and isinstance(body["elapsed_ms"], int)
    assert body["model"] == "test-model"


def test_ask_uses_requested_k_and_model(monkeypatch):
    seen = {}
    monkeypatch.setattr(gateway_app, "retrieve", lambda q, k: (seen.update(k=k) or []))
    monkeypatch.setattr(gateway_app, "generate", lambda q, c, model=None, language=None: (seen.update(model=model) or {"answer": "x", "model": model}))
    client = TestClient(gateway_app.app)
    client.post("/ask", json={"question": "y", "k": 5, "model": "llama3.2:3b"})
    assert seen["k"] == 5
    assert seen["model"] == "llama3.2:3b"


def test_ask_pivot_translates_question_and_answer(monkeypatch):
    calls = {"translate": []}

    def fake_translate(text, target, model=None):
        calls["translate"].append((text, target))
        return f"[{target}]{text}"

    def fake_retrieve(question, k):
        calls["retrieve_q"] = question
        return [{"title": "T", "text": "x", "score": 0.5, "source": "s"}]

    def fake_generate(question, contexts, model=None, language=None):
        calls["gen_language"] = language
        return {"answer": "Antwort v SL", "model": "m"}

    monkeypatch.setattr(gateway_app, "translate", fake_translate)
    monkeypatch.setattr(gateway_app, "retrieve", fake_retrieve)
    monkeypatch.setattr(gateway_app, "generate", fake_generate)

    client = TestClient(gateway_app.app)
    r = client.post("/ask", json={"question": "Was ist ein Sensor?", "language": "nemščina", "pivot": True})
    assert r.status_code == 200
    body = r.json()
    # vprašanje prevedeno v slovenščino za RAG
    assert calls["retrieve_q"].startswith("[slovenščina]")
    assert calls["gen_language"] == "slovenščina"
    # končni odgovor preveden v nemščino
    assert body["answer"].startswith("[nemščina]")
    assert body["translated"] is True


def test_ask_non_slovenian_dropdown_translates_answer(monkeypatch):
    calls = {"translate": []}

    def fake_translate(text, target, model=None):
        calls["translate"].append((text, target))
        return f"[{target}]{text}"

    def fake_retrieve(question, k):
        calls["retrieve_q"] = question
        return [{"title": "T", "text": "x", "score": 0.5, "source": "s"}]

    def fake_generate(question, contexts, model=None, language=None):
        calls["gen_language"] = language
        return {"answer": "Odgovor v slovenščini", "model": "m"}

    monkeypatch.setattr(gateway_app, "translate", fake_translate)
    monkeypatch.setattr(gateway_app, "retrieve", fake_retrieve)
    monkeypatch.setattr(gateway_app, "generate", fake_generate)

    client = TestClient(gateway_app.app)
    r = client.post("/ask", json={"question": "što je senzor", "language": "hrvaščina", "pivot": False})
    assert r.status_code == 200
    body = r.json()
    # brez pivota se vprašanje NE prevaja (RAG na izvirniku), generira pa se v SL
    assert calls["retrieve_q"] == "što je senzor"
    assert calls["gen_language"] == "slovenščina"
    # odgovor se vseeno eksplicitno prevede v ciljni jezik
    assert calls["translate"] == [("Odgovor v slovenščini", "hrvaščina")]
    assert body["answer"] == "[hrvaščina]Odgovor v slovenščini"
    assert body["translated"] is True


def test_ask_escalates_on_false_refusal(monkeypatch):
    calls = []

    def fake_retrieve(question, k):
        return [{"title": "Ultrazvočni senzor", "text": "meri razdaljo", "score": 0.85, "source": "s"}]

    def fake_generate(question, contexts, model=None, language=None):
        calls.append(model)
        if model == "llama3.2:3b":
            return {"answer": "Tega v priročniku ne najdem.", "model": "llama3.2:3b"}
        return {"answer": "Ultrazvočni senzor meri razdaljo do ovire.", "model": model}

    monkeypatch.setattr(gateway_app, "retrieve", fake_retrieve)
    monkeypatch.setattr(gateway_app, "generate", fake_generate)
    client = TestClient(gateway_app.app)
    r = client.post("/ask", json={"question": "a kaj je senzor", "model": "llama3.2:3b"})
    body = r.json()
    assert body["escalated"] is True
    assert "ne najdem" not in body["answer"].lower()
    assert body["model"] == gateway_app.FALLBACK_MODEL
    assert calls == ["llama3.2:3b", gateway_app.FALLBACK_MODEL]


def test_ask_no_escalation_when_context_irrelevant(monkeypatch):
    def fake_retrieve(question, k):
        return [{"title": "Motorji", "text": "x", "score": 0.5, "source": "s"}]

    def fake_generate(question, contexts, model=None, language=None):
        return {"answer": "Tega v priročniku ne najdem.", "model": model}

    monkeypatch.setattr(gateway_app, "retrieve", fake_retrieve)
    monkeypatch.setattr(gateway_app, "generate", fake_generate)
    client = TestClient(gateway_app.app)
    r = client.post("/ask", json={"question": "kakšno je vreme", "model": "llama3.2:3b"})
    body = r.json()
    assert body["escalated"] is False
    assert "ne najdem" in body["answer"].lower()


def test_models_endpoint_adds_times_and_slow_flag(monkeypatch):
    monkeypatch.setattr(
        gateway_app,
        "list_models",
        lambda: {
            "models": [
                {"name": "qwen2.5:14b", "parameter_size": "14.8B", "size": 9000},
                {"name": "llama3.2:3b", "parameter_size": "3.2B", "size": 2000},
                {"name": "gemma3:27b", "parameter_size": "27B", "size": 17000},
            ],
            "default": "qwen2.5:14b",
        },
    )
    client = TestClient(gateway_app.app)
    r = client.get("/models")
    assert r.status_code == 200
    ms = r.json()["models"]
    assert ms[0]["name"] == "llama3.2:3b"  # razvrščeno po času naraščajoče
    assert all("seconds" in m and "slow" in m for m in ms)
    gemma = next(m for m in ms if m["name"] == "gemma3:27b")
    assert gemma["slow"] is True  # 27B -> ~23s
    # prag je 12 s: ~14 s modeli so zdaj tudi "slow" (Subway Surfers)
    assert next(m for m in ms if m["name"] == "qwen2.5:14b")["slow"] is True  # ~13.8s
    assert next(m for m in ms if m["name"] == "llama3.2:3b")["slow"] is False  # ~4.6s


def test_faq_returns_sample_questions():
    client = TestClient(gateway_app.app)
    r = client.get("/faq")
    assert r.status_code == 200
    qs = r.json()["questions"]
    assert any("ultrazvočni" in q.lower() for q in qs)
    assert len(qs) >= 4


def test_health_ok():
    client = TestClient(gateway_app.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
