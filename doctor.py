"""NeuroForge dependency checker and consent-based installer (stdlib only)."""
import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

VERSION="0.5.0"
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
MODEL_FILE=Path.home()/"models"/"qwen-coder.gguf"
MIN_MODEL_BYTES=500_000_000

def termux():
    return "com.termux" in os.environ.get("PREFIX","") or "com.termux" in sys.executable

def describe():
    server=shutil.which("llama-server")
    model=MODEL_FILE.exists() and MODEL_FILE.stat().st_size>=MIN_MODEL_BYTES
    return {
      "version":VERSION,
      "python":platform.python_version(),
      "python_ok":sys.version_info>=(3,10),
      "platform":"termux" if termux() else platform.system().lower(),
      "llama_server":server,
      "model_path":str(MODEL_FILE),
      "model_ready":model,
      "model_bytes":MODEL_FILE.stat().st_size if MODEL_FILE.exists() else 0,
      "model_configured":os.environ.get("NEUROFORGE_MODEL","qwen2.5-coder:1.5b"),
      "api_url":os.environ.get("NEUROFORGE_LLM_URL","http://127.0.0.1:8080/v1/chat/completions"),
      "standard_library_mode":True
    }

def confirm(action, assume_yes=False):
    print("\nProposed action:",action)
    if assume_yes:
        print("Confirmation: pre-approved by explicit --yes flag")
        return True
    try:return input("İcazə verirsən? [y/N]: ").strip().lower() in ("y","yes","b","bəli","he","h")
    except (EOFError,KeyboardInterrupt):return False

def run_command(args, assume_yes=False):
    print("Command:",shutil.join(args) if hasattr(shutil,"join") else " ".join(args))
    if not confirm("Execute the command shown above",assume_yes):return False
    subprocess.run(args,check=True)
    return True

def install_server(assume_yes=False):
    if shutil.which("llama-server"):
        print("llama-server already installed.")
        return True
    if termux() and shutil.which("pkg"):
        return run_command(["pkg","install","llama-cpp","-y"],assume_yes)
    print("Automatic package installation is supported only for Termux.")
    print("Desktop: install llama.cpp or Ollama from its official distribution.")
    return False

def download_model(assume_yes=False):
    if MODEL_FILE.exists() and MODEL_FILE.stat().st_size>=MIN_MODEL_BYTES:
        print("Model file exists:",MODEL_FILE)
        return True
    print("Download source:",MODEL_URL)
    print("Destination:",MODEL_FILE,"(around 1 GB, internet and storage required)")
    if not confirm("Download the GGUF language model",assume_yes):return False
    MODEL_FILE.parent.mkdir(parents=True,exist_ok=True)
    partial=MODEL_FILE.with_suffix(".gguf.part")
    req=urllib.request.Request(MODEL_URL,headers={"User-Agent":"NeuroForge-Installer/0.5"})
    try:
        with urllib.request.urlopen(req,timeout=50) as response, partial.open("wb") as output:
            total=0
            while True:
                chunk=response.read(256*1024)
                if not chunk:break
                output.write(chunk)
                total+=len(chunk)
                if total%(25*1024*1024)<256*1024:
                    print(f"Downloaded {total//1048576} MiB",end="\r",flush=True)
        if partial.stat().st_size<MIN_MODEL_BYTES:
            raise ValueError("Download is incomplete or not a valid model size")
        partial.replace(MODEL_FILE)
        print("\nModel installed:",MODEL_FILE)
        return True
    except Exception as exc:
        print("\nDownload failed:",exc)
        print("Partial file retained:",partial)
        return False

def check_update():
    """Non-invasive version check: fetch raw version tag, never execute remote code."""
    url="https://raw.githubusercontent.com/RuslanSharifov/NeuroForge/main/VERSION"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"NeuroForge/0.5"})
        with urllib.request.urlopen(req,timeout=8) as response:
            remote=response.read(64).decode().strip()
        return {"local":VERSION,"remote":remote,"same":remote==VERSION}
    except Exception as exc:return {"local":VERSION,"remote":None,"error":str(exc)}

def main():
    p=argparse.ArgumentParser(description="NeuroForge check and guided setup")
    p.add_argument("--install",action="store_true",help="Offer installation of missing dependencies")
    p.add_argument("--check-updates",action="store_true",help="Check remote project version")
    p.add_argument("--yes",action="store_true",help="Pre-approve installation actions (use cautiously)")
    args=p.parse_args()
    info=describe()
    print(json.dumps(info,ensure_ascii=False,indent=2))
    if args.check_updates:
        print("GitHub project version:",json.dumps(check_update()))
    if args.install:
        if not info["python_ok"]:
            print("Python >=3.10 required");return 1
        if not info["llama_server"]:install_server(args.yes)
        if not info["model_ready"]:download_model(args.yes)
        print("\nRe-check:")
        print(json.dumps(describe(),ensure_ascii=False,indent=2))
        print("Start local server manually: llama-server -m ~/models/qwen-coder.gguf --alias qwen2.5-coder:1.5b --host 127.0.0.1 --port 8080 -c 2048 -np 1 -t 4")
        print("Then set NEUROFORGE_LLM_URL=http://127.0.0.1:8080/v1/chat/completions and start python tui.py")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
