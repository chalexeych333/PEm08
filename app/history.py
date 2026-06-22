import json
from pathlib import Path
from typing import Any

from .config import settings


history_path = Path(settings.history_file)


def load_history() -> list[dict[str, Any]]:
    if not history_path.exists():
        return []
    try:
        return json.loads(history_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_history(history: list[dict[str, Any]]) -> None:
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def add_history_item(item: dict[str, Any]) -> None:
    history = load_history()
    history.insert(0, item)
    history = history[: settings.max_history_items]
    save_history(history)


def clear_history() -> None:
    save_history([])
