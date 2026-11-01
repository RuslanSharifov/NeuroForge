"""Probe model health and simple text generation without agent tools."""
import json
import os
import time
import urllib.error
import urllib.request
from agent import MODEL, OLLAMA_URL
from model_server import ensure_local_llm

def main():
    print("Checking model server...",flush=True)
    status=ensure_local_llm()
    print("Server:",status,flush=True)
    if not status.get("ready"):return
    payload={"model":MODEL,"messages":[{"role":"user","content":"Say hello briefly."}],
             "max_tokens":32,"temperature":0.3,"stream":False}
    req=urllib.request.Request(OLLAMA_URL,data=json.dumps(payload).encode(),
                               headers={"Content-Type":"application/json"})
    print("Sending 32-token text-only probe...",flush=True)
    started=time.monotonic()
    try:
        with urllib.request.urlopen(req,timeout=90) as response:
            body=json.load(response)
        print("Latency:",round(time.monotonic()-started,1),"seconds",flush=True)
        print("Reply:",str(body.get("choices",body.get("message")))[:1200],flush=True)
    except Exception as exc:
        print("Probe failed:",repr(exc),"after",round(time.monotonic()-started,1),"seconds",flush=True)

if __name__=="__main__":main()
