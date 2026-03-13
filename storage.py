from typing import Any, Dict, List

# Просте зберігання даних у памʼяті процесу
users: Dict[int, Dict[str, Any]] = {}
states: Dict[int, str] = {}
search_state: Dict[int, Dict[str, Any]] = {}
likes_received: Dict[int, List[int]] = {}
premium_users: Dict[int, bool] = {}


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

