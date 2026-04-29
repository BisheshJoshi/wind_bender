import json
import os

_FILE = os.path.join(os.path.dirname(__file__), "scores.json")
MAX_ENTRIES = 10


def load() -> list:
    try:
        with open(_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def add(name: str, score: int) -> list:
    board = load()
    board.append({"name": name[:10].upper(), "score": int(score)})
    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:MAX_ENTRIES]
    with open(_FILE, "w") as f:
        json.dump(board, f)
    return board
