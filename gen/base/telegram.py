from __future__ import annotations

from typing import Iterable

import requests
from django.conf import settings


def bot_enabled() -> bool:
    return bool(getattr(settings, "TELEGRAM_BOT_TOKEN", "").strip())


def _api_url(method: str) -> str:
    token = settings.TELEGRAM_BOT_TOKEN.strip()
    return f"https://api.telegram.org/bot{token}/{method}"


def _normalize_chat_ids(raw_ids: Iterable[str]) -> list[str]:
    result: list[str] = []
    for raw in raw_ids:
        item = str(raw).strip()
        if item and item not in result:
            result.append(item)
    return result


def get_admin_chat_ids() -> list[str]:
    ids = getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", [])
    return _normalize_chat_ids(ids)


def send_telegram_message(chat_id: str | int, text: str) -> tuple[bool, str | None]:
    if not bot_enabled():
        return False, "Telegram bot disabled"

    try:
        payload = {
            "chat_id": str(chat_id).strip(),
            "text": (text or "")[:3900],
            "disable_web_page_preview": True,
        }
        response = requests.post(_api_url("sendMessage"), data=payload, timeout=12)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            return False, data.get("description", "Unknown Telegram API error")
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def broadcast_admin_message(text: str) -> tuple[int, list[str]]:
    sent = 0
    errors: list[str] = []
    for chat_id in get_admin_chat_ids():
        ok, err = send_telegram_message(chat_id, text)
        if ok:
            sent += 1
        else:
            errors.append(f"chat {chat_id}: {err}")
    return sent, errors
