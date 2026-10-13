import os
import json
from pathlib import Path
from typing import Any


def atomic_write_text(filepath: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Writes content to a temporary file in the same directory, then atomically
    replaces the target file using os.replace() to prevent 0-byte file corruption.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = filepath.with_suffix(filepath.suffix + ".tmp")
    with open(tmp_path, "w", encoding=encoding) as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, filepath)


def atomic_write_json(filepath: Path, data: Any, indent: int = 2, encoding: str = "utf-8") -> None:
    """
    Serializes data to formatted JSON and atomically writes it to filepath via temporary file.
    """
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    atomic_write_text(filepath, content, encoding=encoding)
