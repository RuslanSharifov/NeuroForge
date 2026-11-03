"""Windows desktop entrypoint. Python server and web UI run on loopback only."""
import os
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer

def main():
    import webview
    appdata=Path(os.environ.get("LOCALAPPDATA",str(Path.home()))) / "NeuroForge"
    appdata.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault("AI_DB_PATH",str(appdata/"knowledge.db"))
    from server import Handler
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        webview.create_window("NeuroForge",f"http://127.0.0.1:{server.server_port}/",width=1220,height=820,min_size=(380,480))
        webview.start()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

if __name__=="__main__":
    main()
