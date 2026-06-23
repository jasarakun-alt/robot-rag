"""API Gateway (FastAPI). Orkestrira RAG, izbiro modela, jezike (+ pivot prevod); servira UI."""
from __future__ import annotations

import os
import re
import time
from typing import Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

RETRIEVAL_URL = os.environ.get("RETRIEVAL_SERVICE_URL", "http://localhost:8002").rstrip("/")
LLM_URL = os.environ.get("LLM_SERVICE_URL", "http://localhost:8003").rstrip("/")
DEFAULT_TOP_K = int(os.environ.get("TOP_K", "3"))
SLOW_SECONDS = float(os.environ.get("SLOW_SECONDS", "12"))  # nad tem pragom -> Subway Surfers
PIVOT_RAG_LANGUAGE = "slovenščina"  # priročnik je v slovenščini -> RAG poteka v SL
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL", "qwen2.5:14b")  # nadgradnja ob lažni zavrnitvi
ESCALATE_MIN_SCORE = float(os.environ.get("ESCALATE_MIN_SCORE", "0.78"))  # prag relevance za nadgradnjo
REFUSAL_MARKER = "ne najdem"

SAMPLE_QUESTIONS = [
    "Kaj je ultrazvočni senzor?",
    "Kako robot uporablja motorje?",
    "Kaj moramo paziti pri bateriji?",
    "Kako varno uporabljamo robota v razredu?",
]

# Zadnja izmerjena latenca po modelu (model -> sekunde). Self-correct ob uporabi.
MODEL_LATENCY: Dict[str, float] = {}


class AskRequest(BaseModel):
    question: str
    k: Optional[int] = None
    model: Optional[str] = None
    language: Optional[str] = None
    pivot: bool = False


def retrieve(question: str, k: int) -> List[Dict]:
    resp = httpx.post(RETRIEVAL_URL + "/search", json={"query": question, "k": k}, timeout=120)
    resp.raise_for_status()
    return resp.json()["results"]


def generate(question: str, contexts: List[Dict], model: Optional[str] = None, language: Optional[str] = None) -> Dict:
    payload: Dict = {"question": question, "contexts": contexts}
    if model:
        payload["model"] = model
    if language:
        payload["language"] = language
    resp = httpx.post(LLM_URL + "/generate", json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()


def translate(text: str, target_language: str, model: Optional[str] = None) -> str:
    payload: Dict = {"text": text, "target_language": target_language}
    if model:
        payload["model"] = model
    resp = httpx.post(LLM_URL + "/translate", json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["text"]


def list_models() -> Dict:
    resp = httpx.get(LLM_URL + "/models", timeout=30)
    resp.raise_for_status()
    return resp.json()


def estimate_seconds(parameter_size: Optional[str]) -> float:
    """Groba ocena časa odziva iz velikosti modela (B parametrov)."""
    m = re.search(r"([\d.]+)", parameter_size or "")
    billions = float(m.group(1)) if m else 7.0
    return round(billions * 0.8 + 2, 1)


def _is_refusal(text: str) -> bool:
    return REFUSAL_MARKER in (text or "").lower()


def _top_score(contexts: List[Dict]) -> float:
    return max((c.get("score") or 0.0) for c in contexts) if contexts else 0.0


app = FastAPI(title="Robot RAG Gateway")


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway", "retrieval": RETRIEVAL_URL, "llm": LLM_URL}


@app.get("/faq")
def faq():
    return {"questions": SAMPLE_QUESTIONS}


@app.get("/models")
def models():
    try:
        data = list_models()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Napaka pri LLM storitvi: {exc}")
    out = []
    for m in data.get("models", []):
        name = m["name"]
        measured = MODEL_LATENCY.get(name)
        seconds = measured if measured is not None else estimate_seconds(m.get("parameter_size"))
        out.append(
            {
                "name": name,
                "parameter_size": m.get("parameter_size"),
                "size": m.get("size"),
                "seconds": seconds,
                "measured": measured is not None,
                "slow": seconds > SLOW_SECONDS,
            }
        )
    out.sort(key=lambda x: x["seconds"])
    return {"models": out, "default": data.get("default"), "slow_threshold": SLOW_SECONDS}


@app.post("/ask")
def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Vprašanje je prazno.")
    k = req.k or DEFAULT_TOP_K
    language = req.language or "slovenščina"
    model = req.model
    is_slovenian = language.strip().lower() in ("slovenščina", "slovenscina", "slovenian")
    t0 = time.time()
    escalated = False
    try:
        # Vprašanje za RAG: priročnik je v SL. Za tuje jezike lahko vprašanje prevedemo
        # (pivot), sicer se zanesemo na večjezični embedder.
        question_for_rag = req.question
        if not is_slovenian and req.pivot:
            question_for_rag = translate(req.question, PIVOT_RAG_LANGUAGE, model)
        contexts = retrieve(question_for_rag, k)
        # Odgovor VEDNO generiramo v slovenščini (kontekst je SL -> zanesljivo), nato pa
        # ga po potrebi prevedemo.
        gen = generate(question_for_rag, contexts, model=model, language=PIVOT_RAG_LANGUAGE)
        answer_sl = gen["answer"]
        used_model = gen.get("model") or model
        # Lažna zavrnitev: šibek model zavrne, čeprav je kontekst očitno relevanten
        # (visoko ujemanje). Samodejno nadgradimo na zmogljivejši model.
        if (
            _is_refusal(answer_sl)
            and _top_score(contexts) >= ESCALATE_MIN_SCORE
            and (used_model or "").lower() != FALLBACK_MODEL.lower()
        ):
            gen = generate(question_for_rag, contexts, model=FALLBACK_MODEL, language=PIVOT_RAG_LANGUAGE)
            answer_sl = gen["answer"]
            used_model = gen.get("model") or FALLBACK_MODEL
            escalated = True
        answer = answer_sl if is_slovenian else translate(answer_sl, language, model)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Napaka pri storitvah: {exc}")
    elapsed = time.time() - t0
    if used_model and not escalated:
        MODEL_LATENCY[used_model] = round(elapsed, 1)
    return {
        "question": req.question,
        "answer": answer,
        "model": used_model,
        "escalated": escalated,
        "language": language,
        "translated": not is_slovenian,
        "sources": contexts,
        "elapsed_ms": int(elapsed * 1000),
    }


# Statični frontend (chat UI). Mount je zadnji, da ne prekrije API poti.
_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(_STATIC_DIR):
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
