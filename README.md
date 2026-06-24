# Robot RAG — izobraževalni „Robotek" (RAG + lokalni LLM)

Spletni pomočnik, ki učencem odgovarja na vprašanja o robotiki **izključno na podlagi
priročnika** (RAG). Če odgovora v priročniku ni, to pošteno pove in predlaga, naj
vprašajo učitelja. Pod vsakim odgovorom prikaže **uporabljene vire (kontekst)**.

Zgrajeno kot **4 mikrostoritve** (FastAPI), ki se povezujejo med sabo, z razvojem
po **TDD** (testi pred vsako komponento). LLM teče **lokalno prek Ollame**.

## Arhitektura

```
Brskalnik (chat UI)
   │  1. vprašanje
   ▼
API Gateway :8000 ── orkestracija ──┐
   │ 2. /search                     │ 4. /generate (+ kontekst)
   ▼                                ▼
Retrieval :8002                  LLM :8003
   │ 3. embed query                 │ 5. klic
   ▼                                ▼
Embedding :8001                  Ollama (lokalno: qwen2.5:14b)
   │
Vektorski indeks  ◄── indeksiranje priročnika (ob zagonu)
```

Pretok zahteve: brskalnik → gateway → retrieval (→ embedding → indeks) → llm (→ Ollama)
→ **odgovor + viri** nazaj v brskalnik.

| Storitev | Port | Vloga |
|---|---|---|
| `gateway` | 8000 | chat UI + orkestracija (`/ask`, `/faq`, `/health`) |
| `retrieval` | 8002 | chunking priročnika + kosinusno iskanje (`/search`) |
| `embedding` | 8001 | vektorizacija besedila (`/embed`) |
| `llm` | 8003 | generiranje odgovora prek Ollame (`/generate`) |

## Zahteve

- **Python 3.9+**
- **Ollama** z naloženim modelom (priporočeno `qwen2.5:14b` za slovenščino; `llama3.2:3b` je hitrejši)
- (neobvezno) **Docker + Docker Compose**

## Hiter zagon (lokalno, brez dockerja)

```bash
python3 run.py            # realni embeddingi (sentence-transformers, večjezični)
python3 run.py --light    # hash embeddingi (brez torch, hiter zagon)
# odpri http://localhost:8000  ·  ustavi s Ctrl+C
```

`run.py` ustvari `.venv`, namesti vse odvisnosti, po potrebi zažene `ollama serve`
in naloži manjkajoči model, nato zažene vse 4 storitve (logi v `logs/`) ter počaka,
da so pripravljene. `Ctrl+C` čisto ustavi vse.

## Zagon z Dockerjem

```bash
docker compose up --build
# Ollama teče na GOSTITELJU; compose ga doseže prek host.docker.internal
```

## Testi (TDD)

```bash
.venv/bin/pytest -q       # 35 testov (embedding 9, retrieval 11, llm 11, gateway 4)
```

Vsaka mikrostoritev ima teste, pisane **pred** implementacijo (rdeča → zelena):
chunking, kosinusno iskanje, sestava prompta (samo-iz-konteksta + zavrnitev),
parsanje Ollama odgovora, orkestracija gatewaya (z mockiranimi klici).

## API (gateway)

```http
POST /ask     {"question": "...", "k": 3}  ->  {"answer", "model", "sources":[{title,text,score,source}]}
GET  /faq     ->  {"questions": [...]}
GET  /health  ->  {"status":"ok", ...}
```

## Konfiguracija (`.env.example`)

| Spremenljivka | Privzeto | Opis |
|---|---|---|
| `LLM_MODEL` | `qwen2.5:14b` | Ollama model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | naslov Ollame |
| `EMBEDDING_BACKEND` | `sentence-transformers` | ali `hash` (offline/dev) |
| `EMBEDDING_MODEL` | `intfloat/multilingual-e5-small` | večjezični embedder |
| `TOP_K` | `3` | število odlomkov v kontekstu |

## Embedding zaledji

- **`sentence-transformers`** (`multilingual-e5-small`) — privzeto, večjezično, dober
  priklic za slovenščino. Ob prvem zagonu naloži model (~470 MB).
- **`hash`** — deterministični bag-of-words s predznačenim zgoščevanjem; brez odvisnosti,
  za teste/offline. Slabši priklic (semantike ne ujame), a omogoča hiter zagon.

## Napredne funkcije v vmesniku

- **Izbira modela:** spustni meni našteje vse Ollama modele (`GET /models`) z ocenjenim
  oz. izmerjenim časom odziva; po vsakem vprašanju se čas posodobi z dejansko meritvijo.
- **Subway Surfers loading:** za modele, počasnejše od 15 s (npr. `gemma3:27b`, 32B modeli),
  se med čakanjem v ozadju predvaja Subway Surfers video + rotirajoči namigi o robotiki
  (video ID je zamenljiv: `SUBWAY_VIDEO_ID` v `static/app.js`).
- **Jeziki:** neposredna izbira jezika (zmogljivi modeli, npr. `qwen2.5:14b`, jo upoštevajo),
  ali **„Drug jezik (prevod)"** = pivot: vprašanje se prevede v SL za RAG, odgovori v SL,
  nato pa se odgovor prevede v ciljni jezik (deluje tudi s šibkimi modeli).
- **Glas:** 🎤 mikrofon (Web Speech API – SpeechRecognition) za govorno vprašanje in
  🔊 branje odgovora (speechSynthesis; na macOS lokalni sistemski glasovi). Jezik govora
  sledi izbranemu jeziku.

## Ugotovitve (zakaj take izbire)

- **Slovenščina:** večji modeli (`qwen2.5:14b`, `gemma3:27b`) dajo lepšo slovenščino kot
  majhni (`llama3.2:3b`). NVIDIA Nemotron-3-Nano-30B je tekstovni LLM (ne glas, ne slike)
  in slovenščine nima na seznamu uradnih jezikov + zahteva A100/H100 — zato ni izbran.
- **Embeddingi:** realni (e5) bistveno bolje rangirajo kot hash; angleški embedder nad
  slovenščino = slab priklic, zato večjezični.
- **Anti-halucinacija:** sistemski prompt zahteva odgovor samo iz konteksta; brez pokritja
  model reče „Tega v priročniku ne najdem."

## Faza 2 (predvideno, v diagramu)

- **Glas:** implementirano v UI prek Web Speech API (mikrofon + branje odgovora). Za polno
  offline/lokalno različico STT: Whisper (faster-whisper); za lokalni TTS: Piper.
- **Slike/shematike:** vision model (Qwen2.5-VL / GPT-4o) prepozna komponente → RAG poišče
  pravila povezovanja iz priročnika → varnostno opozorilo „preveri z učiteljem".
