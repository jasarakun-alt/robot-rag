"""LLM mikrostoritev (FastAPI): generiranje odgovora, prevajanje, seznam modelov."""
from __future__ import annotations

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import ollama_client
from prompt import build_messages, build_translation_messages


class Context(BaseModel):
    title: str
    text: str
    score: Optional[float] = None
    source: Optional[str] = None


class GenerateRequest(BaseModel):
    question: str
    contexts: List[Context] = []
    model: Optional[str] = None
    language: Optional[str] = None


class GenerateResponse(BaseModel):
    answer: str
    model: str


class TranslateRequest(BaseModel):
    text: str
    target_language: str
    model: Optional[str] = None


app = FastAPI(title="LLM Service")


def _model() -> str:
    return os.environ.get("LLM_MODEL", "qwen2.5:14b")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "llm",
        "model": _model(),
        "ollama": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    }


@app.get("/models")
def models():
    try:
        return {"models": ollama_client.list_models(), "default": _model()}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Ollama napaka: {exc}")


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    model = req.model or _model()
    language = req.language or "slovenščina"
    messages = build_messages(req.question, [c.model_dump() for c in req.contexts], language=language)
    try:
        answer = ollama_client.generate(messages, model=model)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"LLM/Ollama napaka: {exc}")
    return GenerateResponse(answer=answer, model=model)


@app.post("/translate")
def translate(req: TranslateRequest):
    model = req.model or _model()
    messages = build_translation_messages(req.text, req.target_language)
    try:
        text = ollama_client.generate(messages, model=model)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"LLM/Ollama napaka: {exc}")
    return {"text": text, "model": model}
