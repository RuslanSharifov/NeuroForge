"""Offline model catalog sanity checks."""
import unittest
from pathlib import Path
from model_catalog import MODELS,model_info

class ModelCatalogTests(unittest.TestCase):
    def test_models_have_valid_urls_and_aliases(self):
        for key,spec in MODELS.items():
            self.assertTrue(spec["url"].startswith("https://huggingface.co/"))
            self.assertTrue(spec["filename"].endswith(".gguf"))
            self.assertGreater(spec["min_bytes"],100000000)
            self.assertTrue(spec["alias"])
    def test_selected_file_lives_under_models_directory(self):
        self.assertEqual(Path(model_info("chat")["path"]).parent,Path.home()/"models")
if __name__=="__main__":
    unittest.main()
