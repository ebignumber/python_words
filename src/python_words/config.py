from pathlib import Path
import os
import shutil

def get_config_path():
    if os.name == 'nt':
        return Path(os.getenv('LOCALAPPDATA', '')) / "python_words"
    else:
        return Path.home() / ".config" / "python_words"

def initialize_user_config():
    puzzles_dir = get_config_path() / 'Puzzles' / 'Sample'
    if not puzzles_dir.exists():
        puzzles_dir.parent.mkdir(parents=True, exist_ok=True)
        source_dir = Path(__file__).parent / 'Puzzles' / 'Sample'
        print(source_dir)
        if source_dir.exists():
            shutil.copytree(source_dir, puzzles_dir)
