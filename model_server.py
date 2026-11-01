"""Start a local llama.cpp server when needed; never install or download without consent."""
import os
import shutil
import socket
import subprocess
import time
import urllib.parse
from doctor import MODEL_FILE, valid_model

DEFAULT_URL="http://127.0.0.1:8080/v1/chat/completions"

def ready(host="127.0.0.1",port=8080,timeout=0.5):
    try:
        with socket.create_connection((host,port),timeout=timeout): return True
    except OSError: return False

def ensure_local_llm():
    url=os.getenv("NEUROFORGE_LLM_URL",DEFAULT_URL)
    parsed=urllib.parse.urlparse(url)
    if parsed.hostname not in ("127.0.0.1","localhost","::1"):
        return {"ready":True,"managed":False,"note":"External model endpoint configured; not starting a local server"}
    port=parsed.port or (443 if parsed.scheme=="https" else 80)
    if ready(parsed.hostname,port):return {"ready":True,"managed":False}
    if not valid_model():
        return {"ready":False,"error":"GGUF model missing. Run python setup.py to download with consent."}
    executable=shutil.which("llama-server")
    if not executable:
        return {"ready":False,"error":"llama-server missing. Run python setup.py."}
    if port!=8080:
        return {"ready":False,"error":"Custom port configured; start that server manually."}
    log_path=MODEL_FILE.parent/"neuroforge-llama.log"
    logfile=log_path.open("ab")
    cmd=[executable,"-m",str(MODEL_FILE),"--alias",
         os.getenv("NEUROFORGE_MODEL","qwen2.5-coder:1.5b"),
         "--host","127.0.0.1","--port","8080","-c","2048","-np","1","-t","4"]
    try:
        process=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=logfile,stderr=subprocess.STDOUT,
                                 start_new_session=True)
    finally:
        logfile.close()
    for _ in range(40):
        if process.poll() is not None:
            return {"ready":False,"error":"llama-server exited early; inspect "+str(log_path)}
        if ready():return {"ready":True,"managed":True,"pid":process.pid}
        time.sleep(0.5)
    return {"ready":False,"error":"Model still loading; retry shortly. Log: "+str(log_path)}
