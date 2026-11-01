"""Start a local llama.cpp server when needed; never install or download without consent."""
import os
import shutil
import socket
import subprocess
import time
import urllib.parse
import urllib.request
import json
from doctor import MODEL_FILE, valid_model
from model_catalog import model_info

DEFAULT_URL="http://127.0.0.1:8080/v1/chat/completions"

def ready(host="127.0.0.1",port=8080,timeout=0.5):
    try:
        with socket.create_connection((host,port),timeout=timeout): return True
    except OSError: return False

def model_ready(host="127.0.0.1",port=8080):
    """llama.cpp health returns 503 while model is loading."""
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/health",timeout=2) as response:
            data=json.load(response)
            return response.status==200 and data.get("status")=="ok"
    except Exception:
        return False

def wait_until_ready(host,port,seconds=100,process=None):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if process is not None and process.poll() is not None:
            return False
        if model_ready(host,port):
            return True
        time.sleep(1)
    return False

def ensure_local_llm():
    url=os.getenv("NEUROFORGE_LLM_URL",DEFAULT_URL)
    parsed=urllib.parse.urlparse(url)
    if parsed.hostname not in ("127.0.0.1","localhost","::1"):
        return {"ready":True,"managed":False,"note":"External model endpoint configured; not starting a local server"}
    port=parsed.port or (443 if parsed.scheme=="https" else 80)
    if ready(parsed.hostname,port):
        if wait_until_ready(parsed.hostname,port,seconds=100):
            return {"ready":True,"managed":False}
        return {"ready":False,"error":"Model server portu açıqdır, amma /health hələ ready deyil. Log: ~/models/neuroforge-llama.log"}
    selected_model=model_info()
    if not selected_model["installed"]:
        return {"ready":False,"error":"Seçilmiş model yüklənməyib: "+selected_model["title"]+". python setup.py ilə yüklə."}
    executable=shutil.which("llama-server")
    if not executable:
        return {"ready":False,"error":"llama-server missing. Run python setup.py."}
    if port!=8080:
        return {"ready":False,"error":"Custom port configured; start that server manually."}
    log_path=MODEL_FILE.parent/"neuroforge-llama.log"
    logfile=log_path.open("ab")
    cmd=[executable,"-m",selected_model["path"],"--alias",
         selected_model["alias"],
         "--host","127.0.0.1","--port","8080","-c","3072","-np","1","-t","4"]
    try:
        process=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=logfile,stderr=subprocess.STDOUT,
                                 start_new_session=True)
    finally:
        logfile.close()
    if wait_until_ready("127.0.0.1",8080,seconds=100,process=process):
        return {"ready":True,"managed":True,"pid":process.pid}
    if process.poll() is not None:
        return {"ready":False,"error":"llama-server crashed. Log: "+str(log_path)}
    return {"ready":False,"error":"Model still loading; retry shortly. Log: "+str(log_path)}
