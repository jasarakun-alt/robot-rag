#!/usr/bin/env bash
# Ustavi vse lokalno zagnane mikrostoritve.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
shopt -s nullglob
for f in "$ROOT"/run/*.pid; do
  pid="$(cat "$f")"
  if kill "$pid" 2>/dev/null; then
    echo "Ustavljeno $(basename "$f" .pid) (PID $pid)"
  fi
  rm -f "$f"
done
echo "Opomba: Ollama (ollama serve) pustim teči; ustavi jo ročno po želji."
