#!/usr/bin/env python3
"""Namesti odvisnosti in zažene celoten sistem (4 mikrostoritve + Ollama).

Uporaba:
    python3 run.py            # realni embeddingi (sentence-transformers)
    python3 run.py --light    # hiter zagon (hash embeddingi, brez torch)
    python3 run.py --smoke    # zaženi, preveri zdravje, ustavi in končaj (za test)

Ustavitev delujočega sistema: Ctrl+C.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
LIGHT = "--light" in sys.argv
SMOKE = "--smoke" in sys.argv
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:14b")

SERVICES = [
    ("embedding", "embedding_app", 8001),
    ("retrieval", "retrieval_app", 8002),
    ("llm", "llm_app", 8003),
    ("gateway", "gateway_app", 8000),
]


def venv_bin(name: str) -> str:
    sub = "Scripts" if os.name == "nt" else "bin"
    exe = name + (".exe" if os.name == "nt" else "")
    return str(VENV / sub / exe)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def http_ok(url: str, timeout: float = 4) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def wait_health(url: str, tries: int = 90) -> bool:
    for _ in range(tries):
        if http_ok(url):
            return True
        time.sleep(1)
    return False


def ensure_python_deps() -> dict:
    if not VENV.exists():
        print("Ustvarjam virtualno okolje (.venv)...")
        run([sys.executable, "-m", "venv", str(VENV)])
    print("Nameščam Python odvisnosti...")
    run([venv_bin("pip"), "install", "-q", "--upgrade", "pip"])
    run([venv_bin("pip"), "install", "-q", "-r", "requirements-dev.txt"])

    env = os.environ.copy()
    env.update(
        EMBEDDING_SERVICE_URL="http://localhost:8001",
        RETRIEVAL_SERVICE_URL="http://localhost:8002",
        LLM_SERVICE_URL="http://localhost:8003",
        MANUAL_PATH=str(ROOT / "data" / "prirocnik.md"),
        LLM_MODEL=LLM_MODEL,
    )
    if LIGHT:
        env["EMBEDDING_BACKEND"] = "hash"
        print("  --light -> hash embeddingi (brez torch).")
    else:
        env["EMBEDDING_BACKEND"] = "sentence-transformers"
        print("  Nameščam sentence-transformers (prvič lahko traja)...")
        run([venv_bin("pip"), "install", "-q", "-r", "services/embedding/requirements.txt"])
    return env


def ensure_ollama() -> None:
    if shutil.which("ollama") is None:
        print("OPOZORILO: Ollama ni nameščen -> LLM ne bo deloval.")
        print("  Namesti: brew install ollama   (ali https://ollama.com/download)")
        return
    if not http_ok("http://localhost:11434/api/tags", timeout=2):
        print("Zaganjam Ollama...")
        with open(ROOT / "logs" / "ollama.log", "w") as logf:
            subprocess.Popen(["ollama", "serve"], stdout=logf, stderr=subprocess.STDOUT)
        for _ in range(30):
            if http_ok("http://localhost:11434/api/tags", timeout=2):
                break
            time.sleep(1)
    try:
        listed = subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout
    except Exception:
        listed = ""
    if LLM_MODEL not in listed:
        print(f"Nalagam model {LLM_MODEL} (samo prvič, lahko je nekaj GB)...")
        subprocess.run(["ollama", "pull", LLM_MODEL])


def start_services(env: dict) -> list:
    procs = []
    print("Zaganjam mikrostoritve...")
    for name, module, port in SERVICES:
        logf = open(ROOT / "logs" / f"{name}.log", "w")
        proc = subprocess.Popen(
            [venv_bin("uvicorn"), f"{module}:app", "--host", "0.0.0.0", "--port", str(port)],
            cwd=str(ROOT / "services" / name),
            env=env,
            stdout=logf,
            stderr=subprocess.STDOUT,
        )
        procs.append((name, proc, logf))
        print(f"  -> {name} na :{port} (PID {proc.pid})")
    return procs


def stop_all(procs: list, code: int | None = None) -> None:
    print("\nUstavljam storitve...")
    for _, proc, _ in procs:
        if proc.poll() is None:
            proc.terminate()
    for _, proc, logf in procs:
        try:
            proc.wait(timeout=8)
        except Exception:
            proc.kill()
        logf.close()
    print("Ustavljeno.")
    if code is not None:
        sys.exit(code)


def main() -> None:
    os.chdir(ROOT)
    (ROOT / "logs").mkdir(exist_ok=True)

    env = ensure_python_deps()
    ensure_ollama()
    procs = start_services(env)

    signal.signal(signal.SIGINT, lambda *_: stop_all(procs, 0))
    signal.signal(signal.SIGTERM, lambda *_: stop_all(procs, 0))

    print("Čakam, da so storitve pripravljene...")
    all_ok = True
    for name, _module, port in SERVICES:
        ok = wait_health(f"http://localhost:{port}/health")
        print(f"  {'OK ' if ok else 'NI '} {name} :{port}")
        all_ok = all_ok and ok

    print()
    print("✅ Pripravljeno -> http://localhost:8000" if all_ok else "⚠  Nekaj ni pripravljeno; glej logs/*.log")

    if SMOKE:
        stop_all(procs, 0 if all_ok else 1)

    print("Ustavi s Ctrl+C.")
    warned: set = set()
    while True:
        time.sleep(2)
        for name, proc, _ in procs:
            if proc.poll() is not None and name not in warned:
                warned.add(name)
                print(f"⚠  Storitev '{name}' se je ustavila (koda {proc.returncode}). Glej logs/{name}.log")


if __name__ == "__main__":
    main()
