import pytest
from python_words.config import get_config_path
import os
from pathlib import Path

def test_get_config_path():
    if os.name == 'nt':
        assert get_config_path() == Path(os.getenv('LOCALAPPDATA', '')) / "python_words"
    else:
        assert get_config_path() == Path.home() / ".config" / "python_words"

