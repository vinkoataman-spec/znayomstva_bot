import time
from typing import Any, Dict, List, Optional

# Просте зберігання даних у памʼяті процесу
users: Dict[int, Dict[str, Any]] = {}
states: Dict[int, str] = {}
search_state: Dict[int, Dict[str, Any]] = {}
likes_received: Dict[int, List[int]] = {}
# premium_users[user_id] = unix timestamp when premium ends (seconds). 0/None = no premium.
premium_users: Dict[int, int] = {}
admin_state: Dict[int, Dict[str, Any]] = {}


def ensure_user(chat_id: int) -> Dict[str, Any]:
    if chat_id not in users:
        users[chat_id] = {
            "gender": None,
            "name": None,
            "age": None,
            "photo_file_id": None,
        }
    return users[chat_id]


def is_profile_complete(chat_id: int) -> bool:
    profile = users.get(chat_id)
    if not profile:
        return False
    return all(
        profile.get(key) is not None
        for key in ("gender", "name", "age", "photo_file_id")
    )


def now_ts() -> int:
    return int(time.time())


def has_premium(chat_id: int) -> bool:
    return premium_users.get(chat_id, 0) > now_ts()


def set_premium(chat_id: int, days: int) -> int:
    """
    Grants/extends premium for N days. Returns new expiry timestamp.
    """
    current_expiry = premium_users.get(chat_id, 0)
    base = current_expiry if current_expiry > now_ts() else now_ts()
    new_expiry = base + days * 24 * 60 * 60
    premium_users[chat_id] = new_expiry
    return new_expiry


def premium_expiry(chat_id: int) -> Optional[int]:
    exp = premium_users.get(chat_id, 0)
    return exp if exp > 0 else None

