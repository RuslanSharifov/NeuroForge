from unittest.mock import patch
import tui

def test_crop_width():
    assert len(tui.crop("abcdefghij", 5)) <= 5

def test_width_minimum():
    with patch("tui.shutil.get_terminal_size") as size:
        size.return_value.columns=20
        assert tui.width()==32
