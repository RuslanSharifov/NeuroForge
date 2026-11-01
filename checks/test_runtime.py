"""Standard-library tests for workspace security and approval-gated edits."""
import os
import tempfile
import unittest
from pathlib import Path

_TEMP=tempfile.TemporaryDirectory()
os.environ["AI_DB_PATH"]=str(Path(_TEMP.name)/"test.db")
os.environ["NEUROFORGE_WORKSPACE"]=_TEMP.name

from agent_runtime import tool_list_files, tool_read_file, propose_edit, decide_edit, inside

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.path=Path(_TEMP.name)/"example.html"
        self.path.write_text("<div>Hi</div>",encoding="utf-8")
    def test_read_and_proposal(self):
        self.assertIn("example.html",[x["path"] for x in tool_list_files()])
        self.assertIn("<div>",tool_read_file("example.html")["content"])
        edit=propose_edit("example.html","<header>Hi</header>")
        self.assertEqual(edit["status"],"needs_approval")
        self.assertEqual(self.path.read_text(),"<div>Hi</div>")
        self.assertEqual(decide_edit(edit["id"],True)["status"],"applied")
        self.assertEqual(self.path.read_text(),"<header>Hi</header>")
    def test_path_security(self):
        with self.assertRaises(ValueError):inside("../outside.txt")
    def test_conflict(self):
        edit=propose_edit("example.html","<main>hello</main>")
        self.path.write_text("other",encoding="utf-8")
        with self.assertRaises(ValueError):decide_edit(edit["id"],True)

if __name__=="__main__":
    unittest.main()
