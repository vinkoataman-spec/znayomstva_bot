from typing import Any, Dict


def main_menu_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [
                {"text": "🔍 Пошук"},
                {"text": "👤 Мій профіль"},
            ],
            [
                {"text": "❤️ Лайки"},
                {"text": "⭐ Підписка"},
            ],
            [
                {"text": "❓ Допомога"},
            ],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def gender_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Чоловік"}, {"text": "Жінка"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }


def buy_premium_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Купити преміум"}],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def search_actions_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Лайк"}, {"text": "Дизлайк"}],
            [{"text": "Наступний"}, {"text": "Вийти з пошуку"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def profile_actions_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Редагувати мій профіль"}],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def edit_profile_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Змінити імʼя"}],
            [{"text": "Змінити фото"}],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def likes_menu_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Переглянути, хто мене лайкнув"}],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def subscription_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [
                {"text": "🗓️ Підписка на тиждень"},
                {"text": "📅 Підписка на місяць"},
            ],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }

