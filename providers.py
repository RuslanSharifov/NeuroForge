"""Opt-in Gemini provider. API key lives in a local user-private config, never in Git."""
import getpass
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

CONFIG=Path.home()/".neuroforge"/"provider.json"
DEFAULT_MODEL="gemini-2.5-flash"

def config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError,ValueError): return {"provider":"local","gemini_model":DEFAULT_MODEL}

def save(values):
    CONFIG.parent.mkdir(parents=True,exist_ok=True)
    if not CONFIG.exists():
        CONFIG.touch(mode=0o600)
    CONFIG.write_text(json.dumps(values,ensure_ascii=False),encoding="utf-8")
    try:os.chmod(CONFIG,0o600)
    except OSError:pass

def provider():
    return os.environ.get("NEUROFORGE_PROVIDER",config().get("provider","local"))

def gemini_key():
    return os.environ.get("GEMINI_API_KEY") or config().get("gemini_api_key","")

def menu():
    data=config()
    print("\nAI provayderi:",provider())
    print("1 — Lokal GGUF (internetsiz)\n2 — Gemini API (internet tələb edir)\n3 — API key-i sil\n0 — Geri")
    choice=input("Seçim > ").strip()
    if choice=="1":
        data["provider"]="local"
    elif choice=="2":
        print("Key heç vaxt GitHub-a yüklənməyəcək. Terminaldan daxil et.")
        key=getpass.getpass("Gemini API key (boş = mövcudu saxla): ").strip()
        if key:data["gemini_api_key"]=key
        if not (data.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")):
            print("API key yoxdur.");return
        data["provider"]="gemini"
        name=input("Gemini model (Enter = gemini-2.5-flash): ").strip()
        data["gemini_model"]=name or data.get("gemini_model",DEFAULT_MODEL)
    elif choice=="3":
        data.pop("gemini_api_key",None)
        data["provider"]="local"
    else:return
    save(data)
    print("Yadda saxlandı. Provayder:",data["provider"])

def generate(messages):
    key=gemini_key()
    if not key:raise RuntimeError("Gemini API key yoxdur. Provayder menyusundan daxil et.")
    data=config()
    model=data.get("gemini_model",DEFAULT_MODEL)
    if not model.replace("-","").replace(".","").isalnum():
        raise ValueError("Invalid Gemini model")
    contents=[]
    system=[]
    for msg in messages:
        if msg.get("role")=="system":
            system.append(str(msg.get("content","")))
        elif msg.get("role") in ("assistant","user"):
            contents.append({"role":"model" if msg["role"]=="assistant" else "user",
                             "parts":[{"text":str(msg.get("content",""))}]})
    body={"contents":contents,"systemInstruction":{"parts":[{"text":"\n".join(system)}]},
          "generationConfig":{"maxOutputTokens":512,"temperature":0.55}}
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    request=urllib.request.Request(url,data=json.dumps(body).encode("utf-8"),headers={
        "Content-Type":"application/json","x-goog-api-key":key})
    try:
        with urllib.request.urlopen(request,timeout=120) as response:
            result=json.load(response)
    except urllib.error.HTTPError as exc:
        details=exc.read(1000).decode("utf-8","replace")
        raise RuntimeError(f"Gemini HTTP {exc.code}: {details[:450]}") from exc
    candidates=result.get("candidates") or []
    if not candidates:raise RuntimeError("Gemini cavab generasiya etmədi")
    parts=candidates[0].get("content",{}).get("parts",[])
    text="".join(p.get("text","") for p in parts).strip()
    if not text:raise RuntimeError("Gemini boş cavab qaytardı")
    return {"message":{"role":"assistant","content":text},"model":model}
