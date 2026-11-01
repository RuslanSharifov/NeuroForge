"""Dependency-free local web server for NeuroForge (Termux/Windows/Linux)."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from model_server import ensure_local_llm
from agent_runtime import agent_run, pending_edits, decide_edit
from agent import respond, import_github_skill, import_github_repo, skills, set_skill_active
from core import (
    HTTPException, KnowledgeIn, KnowledgePatch, ChatIn, FeedbackIn,
    db, health, create_knowledge, list_knowledge, get_knowledge,
    patch_knowledge, delete_knowledge, history, chat, create_feedback,
    list_feedback, approve_feedback
)

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body=json.dumps(data,ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def do_PATCH(self):
        self.dispatch("PATCH")

    def do_DELETE(self):
        self.dispatch("DELETE")

    def dispatch(self, method):
        # Reject cross-site state-changing requests; the API is local and unauthenticated.
        if method in ("POST","PATCH","DELETE"):
            from urllib.parse import urlparse
            origin=self.headers.get("Origin")
            if origin:
                parsed=urlparse(origin)
                host=self.headers.get("Host","").lower()
                if parsed.scheme!="http" or parsed.netloc.lower()!=host:
                    return self.send_json({"detail":"Invalid origin"},403)
        path=urlsplit(self.path).path.rstrip("/") or "/"
        if method=="GET" and path=="/logo.svg":
            raw=(Path(__file__).parent/"web"/"logo.svg").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","image/svg+xml")
            self.send_header("Content-Length",str(len(raw)))
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers()
            self.wfile.write(raw)
            return
        if method=="GET" and path=="/":
            raw=(Path(__file__).parent/"web"/"index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(raw)))
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers()
            self.wfile.write(raw)
            return
        try:
            with db(): pass
            size=int(self.headers.get("Content-Length","0"))
            if size > 1024*1024: return self.send_json({"detail":"Body too large"},413)
            payload=json.loads(self.rfile.read(size)) if size else {}
            if not isinstance(payload,dict): raise ValueError("JSON object required")
            segments=path.strip("/").split("/")
            result=None
            status=200
            if (method,path)==("GET","/health"): result=health()
            elif path=="/knowledge":
                if method=="GET": result=list_knowledge()
                elif method=="POST":
                    result=create_knowledge(KnowledgeIn(**payload));status=201
            elif segments[0]=="knowledge" and len(segments)>=2 and segments[1].isdigit():
                ident=int(segments[1])
                if len(segments)==2:
                    if method=="GET": result=get_knowledge(ident)
                    elif method=="PATCH": result=patch_knowledge(ident,KnowledgePatch(**payload))
                    elif method=="DELETE": result=delete_knowledge(ident)
                elif len(segments)==3 and segments[2]=="history" and method=="GET":
                    result=history(ident)
            elif (method,path)==("POST","/agent/run"):
                status=ensure_local_llm()
                if not status["ready"]:raise HTTPException(503,status.get("error","Local model unavailable"))
                result=agent_run(str(payload.get("message","")))
            elif (method,path)==("GET","/agent/edits"):
                result=pending_edits()
            elif len(segments)==4 and segments[:2]==["agent","edits"] and segments[3] in ("approve","reject") and method=="POST":
                result=decide_edit(segments[2],segments[3]=="approve")
            elif (method,path)==("POST","/agent/chat"):
                result=respond(str(payload.get("message","")))
            elif (method,path)==("GET","/agent/skills"):
                result=skills()
            elif (method,path)==("POST","/agent/skills/import"):
                result=(import_github_repo(str(payload.get("url",""))) if "/blob/" not in str(payload.get("url","")) else import_github_skill(str(payload.get("url",""))));status=201
            elif len(segments)==4 and segments[:2]==["agent","skills"] and segments[2].isdigit() and segments[3]=="activate" and method=="POST":
                result=set_skill_active(int(segments[2]),bool(payload.get("active",False)))
            elif (method,path)==("POST","/chat"):
                result=chat(ChatIn(**payload))
            elif path=="/feedback":
                if method=="GET":result=list_feedback()
                elif method=="POST":
                    result=create_feedback(FeedbackIn(**payload));status=201
            elif len(segments)==3 and segments[0]=="feedback" and segments[1].isdigit() and segments[2]=="approve" and method=="POST":
                result=approve_feedback(int(segments[1]))
            if result is None: raise HTTPException(404,"Route not found")
            self.send_json(result,status)
        except HTTPException as e:
            self.send_json({"detail":e.detail},e.status_code)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
            self.send_json({"detail":str(e)},422)
        except Exception:
            self.send_json({"detail":"Internal server error"},500)

def run():
    host=os.getenv("NEUROFORGE_HOST","127.0.0.1")
    port=int(os.getenv("PORT","8000"))
    with ThreadingHTTPServer((host,port),Handler) as server:
        print(f"NeuroForge web: http://{host}:{port} (Ctrl+C to stop)")
        server.serve_forever()

if __name__=="__main__":
    run()
