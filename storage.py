import time
from typing import Any, Dict, List, Optional

WEEK_SECONDS = 7 * 24 * 60 * 60
MAX_FREE_LIKES_PER_WEEK = 20

# Просте зберігання даних у памʼяті процесу
users: Dict[int, Dict[str, Any]] = {}
states: Dict[int, str] = {}
search_state: Dict[int, Dict[str, Any]] = {}
likes_received: Dict[int, List[int]] = {}
# premium_users[user_id] = unix timestamp when premium ends (seconds). 0/None = no premium.
premium_users: Dict[int, int] = {}
admin_state: Dict[int, Dict[str, Any]] = {}
# like_quota[user_id] = {"count": int, "reset_at": ts}
like_quota: Dict[int, Dict[str, int]] = {}


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


def can_use_free_like(chat_id: int) -> bool:
    """
    Checks if a non-premium user can still use like/dislike this week.
    """
    data = like_quota.get(chat_id)
    now = now_ts()
    if not data or now >= data.get("reset_at", 0):
        # new week window
        like_quota[chat_id] = {"count": 0, "reset_at": now + WEEK_SECONDS}
        return True
    return data.get("count", 0) < MAX_FREE_LIKES_PER_WEEK


def register_free_like(chat_id: int) -> int:
    """
    Increments like/dislike counter for non-premium user.
    Returns new count in current week window.
    """
    now = now_ts()
    data = like_quota.get(chat_id)
    if not data or now >= data.get("reset_at", 0):
        data = {"count": 0, "reset_at": now + WEEK_SECONDS}
        like_quota[chat_id] = data
    data["count"] = data.get("count", 0) + 1
    return data["count"]

