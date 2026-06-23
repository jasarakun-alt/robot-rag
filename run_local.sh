#!/usr/bin/env bash
# Lokalni zagon vseh 4 mikrostoritev (brez dockerja) + Ollama.
# Uporaba:  ./run_local.sh           (realni embeddingi prek sentence-transformers)
#           LIGHT=1 ./run_local.sh   (hiter zagon, hash embeddingi, brez torch)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
mkdir -p logs run

PY="${PY:-python3}"
VENV="$ROOT/.venv"
[ -d "$VENV" ] || "$PY" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install -q --upgrade pip
pip install -q -r requirements-dev.txt

if [ "${LIGHT:-0}" = "1" ]; then
  export EMBEDDING_BACKEND=hash
  echo "LIGHT=1 -> uporabljam hash embeddinge (brez torch)."
else
  export EMBEDDING_BACKEND=sentence-transformers
  echo "Nameščam realne embeddinge (sentence-transformers, lahko traja ob prvem zagonu)..."
  pip install -q -r services/embedding/requirements.txt
fi

# Ollama na gostitelju
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "Zaganjam Ollama..."
  (ollama serve >"$ROOT/logs/ollama.log" 2>&1 &) || echo "OPOZORILO: Ollama ni na voljo."
  sleep 3
fi

export EMBEDDING_SERVICE_URL=http://localhost:8001
export RETRIEVAL_SERVICE_URL=http://localhost:8002
export LLM_SERVICE_URL=http://localhost:8003
export MANUAL_PATH="$ROOT/data/prirocnik.md"
export LLM_MODEL="${LLM_MODEL:-qwen2.5:14b}"

start() {  # ime modul port
  echo "  -> $1 na :$3"
  ( cd "services/$1" && exec "$VENV/bin/uvicorn" "$2:app" --host 0.0.0.0 --port "$3" ) \
    >"$ROOT/logs/$1.log" 2>&1 &
  echo $! > "$ROOT/run/$1.pid"
}

echo "Zaganjam mikrostoritve..."
start embedding embedding_app 8001
start retrieval retrieval_app 8002
start llm       llm_app       8003
sleep 2
start gateway   gateway_app   8000

echo ""
echo "Pripravljeno. Odpri:  http://localhost:8000"
echo "Dnevniki: $ROOT/logs/*.log   |   Ustavi: ./stop_local.sh"
