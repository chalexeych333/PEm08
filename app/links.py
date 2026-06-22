import re
from pathlib import Path

from .config import settings


def normalize_link(line: str) -> str:
    cleaned = line.strip()
    cleaned = re.sub(r"^\s*\d+\.\s*", "", cleaned)
    return cleaned


def load_links() -> list[str]:
    path = Path(settings.data_links_path)
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    lines = [normalize_link(line) for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    return lines
