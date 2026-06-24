"""Ollama klient: payload, parsanje odgovora, parsanje modelov."""
from __future__ import annotations

import pytest

from ollama_client import build_payload, parse_chat_response, parse_tags


def test_build_payload_basics():
    msgs = [{"role": "user", "content": "živjo"}]
    p = build_payload(msgs, model="qwen2.5:14b", temperature=0.1)
    assert p["model"] == "qwen2.5:14b"
    assert p["messages"] == msgs
    assert p["stream"] is False
    assert p["options"]["temperature"] == 0.1


def test_parse_chat_response_extracts_content():
    data = {"message": {"role": "assistant", "content": "Odgovor robota."}, "done": True}
    assert parse_chat_response(data) == "Odgovor robota."


def test_parse_chat_response_strips_whitespace():
    data = {"message": {"content": "  besedilo  \n"}}
    assert parse_chat_response(data) == "besedilo"


def test_parse_chat_response_bad_format_raises():
    with pytest.raises(Exception):
        parse_chat_response({"unexpected": True})


def test_parse_tags_extracts_models():
    data = {
        "models": [
            {"name": "qwen2.5:14b", "size": 9000, "details": {"parameter_size": "14.8B", "family": "qwen2"}},
            {"name": "llama3.2:3b", "size": 2000, "details": {"parameter_size": "3.2B"}},
        ]
    }
    ms = parse_tags(data)
    assert [m["name"] for m in ms] == ["qwen2.5:14b", "llama3.2:3b"]
    assert ms[0]["parameter_size"] == "14.8B"


def test_parse_tags_empty():
    assert parse_tags({}) == []
