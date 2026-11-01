"""NeuroForge stdlib-only offline knowledge engine."""
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.getenv("AI_DB_PATH", str(Path(__file__).with_name("knowledge.db"))))


def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS knowledge (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          question TEXT NOT NULL, answer TEXT NOT NULL,
          category TEXT NOT NULL DEFAULT 'general', enabled INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS revisions (
          id INTEGER PRIMARY KEY AUTOINCREMENT, knowledge_id INTEGER NOT NULL,
          old_question TEXT, old_answer TEXT, new_question TEXT, new_answer TEXT,
          changed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS feedback (
          id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT NOT NULL,
          suggested_answer TEXT NOT NULL, approved INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        );
        """)
        yield c
        c.commit()
    finally:
        c.close()

class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

class Model:
    def __init__(self, **kwargs):
        self._values = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    def model_dump(self, exclude_unset=False):
        return dict(self._values)

class KnowledgeIn(Model):
    def __init__(self, question, answer, category="general", enabled=True):
        if len(question.strip()) < 3 or not answer.strip():
            raise ValueError("question and answer are required")
        super().__init__(question=question, answer=answer, category=category, enabled=enabled)

class KnowledgePatch(Model):
    pass

class ChatIn(Model):
    def __init__(self, message):
        if not message.strip(): raise ValueError("message is required")
        super().__init__(message=message)

class FeedbackIn(Model):
    def __init__(self, prompt, suggested_answer):
        if not prompt.strip() or not suggested_answer.strip(): raise ValueError("feedback fields required")
        super().__init__(prompt=prompt, suggested_answer=suggested_answer)

def health():
    return {"status": "ok", "mode": "local", "external_api_required": False}

def create_knowledge(item: KnowledgeIn):
    with db() as c:
        cur = c.execute(
            "INSERT INTO knowledge(question,answer,category,enabled,created_at,updated_at) VALUES (?,?,?,?,?,?)",
            (item.question,item.answer,item.category,int(item.enabled),now(),now()))
        return dict(c.execute("SELECT * FROM knowledge WHERE id=?", (cur.lastrowid,)).fetchone())

def list_knowledge():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM knowledge ORDER BY id DESC")]

def get_knowledge(item_id: int):
    with db() as c:
        row = c.execute("SELECT * FROM knowledge WHERE id=?", (item_id,)).fetchone()
        if not row: raise HTTPException(404, "Knowledge not found")
        return dict(row)

def patch_knowledge(item_id: int, item: KnowledgePatch):
    with db() as c:
        old = c.execute("SELECT * FROM knowledge WHERE id=?", (item_id,)).fetchone()
        if not old: raise HTTPException(404, "Knowledge not found")
        changes = item.model_dump(exclude_unset=True)
        if changes:
            new = {**dict(old),**changes}
            c.execute("UPDATE knowledge SET question=?,answer=?,category=?,enabled=?,updated_at=? WHERE id=?",
                (new["question"],new["answer"],new["category"],int(new["enabled"]),now(),item_id))
            c.execute("INSERT INTO revisions(knowledge_id,old_question,old_answer,new_question,new_answer,changed_at) VALUES(?,?,?,?,?,?)",
                (item_id,old["question"],old["answer"],new["question"],new["answer"],now()))
        return dict(c.execute("SELECT * FROM knowledge WHERE id=?", (item_id,)).fetchone())

def delete_knowledge(item_id: int):
    with db() as c:
        if not c.execute("DELETE FROM knowledge WHERE id=?", (item_id,)).rowcount:
            raise HTTPException(404, "Knowledge not found")
        return {"deleted": True, "id": item_id}

def history(item_id: int):
    with db() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM revisions WHERE knowledge_id=? ORDER BY id DESC", (item_id,))]

def tokens(s: str):
    return set(re.findall(r"\w+", s.casefold(), flags=re.UNICODE))

def chat(item: ChatIn):
    query = tokens(item.message)
    with db() as c:
        rows = c.execute("SELECT * FROM knowledge WHERE enabled=1").fetchall()
    ranked = []
    for row in rows:
        words = tokens(row["question"])
        union = query | words
        score = len(query & words) / len(union) if union else 0
        if score: ranked.append((score,row))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    if not ranked or ranked[0][0] < .25:
        return {"answer": "Bu barədə hələ etibarlı bilik öyrədilməyib.",
                "source_id": None, "confidence": 0, "method": "lexical_retrieval"}
    score, row = ranked[0]
    return {"answer":row["answer"], "source_id":row["id"],
            "confidence":round(score,3), "method":"lexical_retrieval"}

def create_feedback(item: FeedbackIn):
    with db() as c:
        cur = c.execute("INSERT INTO feedback(prompt,suggested_answer,created_at) VALUES (?,?,?)",
                        (item.prompt,item.suggested_answer,now()))
        return {"feedback_id":cur.lastrowid,"approved":False}

def list_feedback():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM feedback ORDER BY id DESC")]

def approve_feedback(feedback_id: int):
    with db() as c:
        row = c.execute("SELECT * FROM feedback WHERE id=?", (feedback_id,)).fetchone()
        if not row: raise HTTPException(404, "Feedback not found")
        if row["approved"]: raise HTTPException(409, "Already approved")
        cur = c.execute(
            "INSERT INTO knowledge(question,answer,category,enabled,created_at,updated_at) VALUES (?,?,?,?,?,?)",
            (row["prompt"],row["suggested_answer"],"approved_feedback",1,now(),now()))
        c.execute("UPDATE feedback SET approved=1 WHERE id=?", (feedback_id,))
        return {"approved":True,"knowledge_id":cur.lastrowid}
