"""Zero-dependency tests: python -m unittest discover -s checks -v."""
import os
import tempfile
import unittest
from pathlib import Path

with tempfile.TemporaryDirectory() as temp:
    pass
os.environ["AI_DB_PATH"]=str(Path(tempfile.gettempdir())/"neuroforge_unit_test_"+str(os.getpid())+".db")
from core import (
    KnowledgeIn,KnowledgePatch,ChatIn,FeedbackIn,create_knowledge,chat,
    patch_knowledge,history,create_feedback,approve_feedback,delete_knowledge
)
from tui import crop

class CoreTests(unittest.TestCase):
    def test_knowledge(self):
        row=create_knowledge(KnowledgeIn(question="Python list nədir?",answer="Kolleksiya"))
        key=row["id"]
        self.assertEqual(chat(ChatIn(message="Python list nədir?"))["source_id"],key)
        patch_knowledge(key,KnowledgePatch(enabled=False))
        self.assertEqual(len(history(key)),1)
        self.assertIsNone(chat(ChatIn(message="Python list nədir?"))["source_id"])
        delete_knowledge(key)

    def test_feedback(self):
        row=create_feedback(FeedbackIn(prompt="NeuroForge nədir?",suggested_answer="Lokal AI"))
        self.assertTrue(approve_feedback(row["feedback_id"])["approved"])

    def test_terminal(self):
        self.assertLessEqual(len(crop("abcdefghijk",5)),5)

if __name__=="__main__":
    unittest.main()
