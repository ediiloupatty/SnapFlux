import json
import os
from typing import Dict

STATE_PATH = os.path.join("akun", "nik_state.json")


def _load_raw_state() -> Dict[str, int]:
    try:
        if not os.path.exists(STATE_PATH):
            return {}
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {str(k): int(v) for k, v in data.items() if isinstance(v, int) or (isinstance(v, str) and v.isdigit())}
            return {}
    except Exception:
        return {}


def _save_raw_state(state: Dict[str, int]) -> None:
    try:
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        # Silent fail; runtime should continue even if persistence fails
        pass


def get_next_index(username: str, total_nik: int) -> int:
    if total_nik <= 0:
        return 0
    state = _load_raw_state()
    idx = int(state.get(username, 0)) % total_nik
    return idx


def advance_next_index(username: str, total_nik: int, step: int = 1) -> int:
    if total_nik <= 0:
        return 0
    state = _load_raw_state()
    current = int(state.get(username, 0))
    new_val = (current + max(1, int(step))) % total_nik
    state[username] = new_val
    _save_raw_state(state)
    return new_val


