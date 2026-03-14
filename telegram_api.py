from typing import Any, Dict, Optional

import requests

from config import API_URL


def send_message(
    chat_id: int,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
) -> None:
    url = f"{API_URL}sendMessage"
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to send message: {exc}")


def send_photo(
    chat_id: int,
    photo_file_id: str,
    caption: str = "",
    reply_markup: Optional[Dict[str, Any]] = None,
) -> None:
    url = f"{API_URL}sendPhoto"
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "photo": photo_file_id,
    }
    if caption:
        payload["caption"] = caption
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to send photo: {exc}")


def send_sticker(chat_id: int, sticker_id: str) -> None:
    """
    Надсилання стікера за file_id.
    file_id можна взяти, надіславши стікер боту й подивившись update.
    """
    url = f"{API_URL}sendSticker"
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "sticker": sticker_id,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to send sticker: {exc}")


def get_updates(offset: Optional[int] = None) -> Dict[str, Any]:
    url = f"{API_URL}getUpdates"
    params: Dict[str, Any] = {"timeout": 100, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=110)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"Failed to get updates: {exc}")
        return {}

