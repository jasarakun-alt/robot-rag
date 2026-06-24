"""Sestava prompta (samo-iz-konteksta, jezik) in prevajanje."""
from __future__ import annotations

from prompt import build_messages, build_translation_messages

CTX = [
    {"title": "Ultrazvočni senzor", "text": "Meri razdaljo do ovire z odbojem zvoka."},
    {"title": "Baterije", "text": "Pazimo na polariteto in ne kratko stikamo."},
]


def test_messages_have_system_and_user():
    msgs = build_messages("Kaj je ultrazvočni senzor?", CTX)
    roles = [m["role"] for m in msgs]
    assert "system" in roles
    assert roles[-1] == "user"


def test_question_is_included():
    msgs = build_messages("Kako deluje ultrazvočni senzor?", CTX)
    joined = " ".join(m["content"] for m in msgs)
    assert "Kako deluje ultrazvočni senzor?" in joined


def test_context_titles_and_text_included():
    msgs = build_messages("vprašanje", CTX)
    joined = " ".join(m["content"] for m in msgs)
    assert "Ultrazvočni senzor" in joined
    assert "odbojem zvoka" in joined
    assert "polariteto" in joined


def test_strict_context_only_instruction():
    msgs = build_messages("vprašanje", CTX)
    system = next(m["content"] for m in msgs if m["role"] == "system")
    assert "IZKLJUČNO" in system
    assert "ne najdem" in system.lower()


def test_empty_context_has_marker():
    msgs = build_messages("vprašanje brez vira", [])
    joined = " ".join(m["content"] for m in msgs)
    assert "ni najdenega konteksta" in joined.lower()


def test_default_language_is_slovenian():
    system = next(m["content"] for m in build_messages("v", CTX) if m["role"] == "system")
    assert "slovenščina" in system.lower()


def test_language_instruction_included():
    system = next(m["content"] for m in build_messages("v", CTX, language="angleščina") if m["role"] == "system")
    assert "angleščina" in system


def test_translation_messages():
    msgs = build_translation_messages("Pozdravljen", "angleščina")
    assert msgs[-1]["content"] == "Pozdravljen"
    assert "angleščina" in msgs[0]["content"]
