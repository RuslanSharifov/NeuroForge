import os
import tempfile

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["AI_DB_PATH"] = path

from fastapi.testclient import TestClient
from main import app

def test_crud_and_chat():
    with TestClient(app) as c:
        assert c.get("/health").json()["status"] == "ok"
        r = c.post("/knowledge", json={"question":"Python list nədir?", "answer":"Dəyişən kolleksiyadır."})
        assert r.status_code == 201
        ident = r.json()["id"]
        assert c.post("/chat", json={"message":"Python list nədir?"}).json()["source_id"] == ident
        assert c.patch(f"/knowledge/{ident}", json={"enabled":False}).status_code == 200
        assert c.post("/chat", json={"message":"Python list nədir?"}).json()["source_id"] is None
        assert len(c.get(f"/knowledge/{ident}/history").json()) == 1
        assert c.delete(f"/knowledge/{ident}").status_code == 200

def test_feedback():
    with TestClient(app) as c:
        res = c.post("/feedback", json={"prompt":"JWT nədir?", "suggested_answer":"Token formatıdır."})
        ident = res.json()["feedback_id"]
        approved = c.post(f"/feedback/{ident}/approve")
        assert approved.status_code == 200
        assert c.post(f"/feedback/{ident}/approve").status_code == 409

def test_dashboard():
    with TestClient(app) as c:
        assert c.get("/").status_code == 200
        assert "NeuroForge" in c.get("/").text
