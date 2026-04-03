from typing import Any, Dict

CITIES = [
    "Вінницька обл",
    "Волинська обл",
    "Дніпропетровська обл",
    "Донецька обл",
    "Житомирська обл",
    "Закарпатська обл",
    "Запорізька обл",
    "Івано-Франківська обл",
    "Київська обл",
    "Кіровоградська обл",
    "Луганська обл",
    "Львівська обл",
    "Миколаївська обл",
    "Одеська обл",
    "Полтавська обл",
    "Рівненська обл",
    "Сумська обл",
    "Тернопільська обл",
    "Харківська обл",
    "Херсонська обл",
    "Хмельницька обл",
    "Черкаська обл",
    "Чернівецька обл",
    "Чернігівська обл",
    "м. Київ",
]


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
            [{"text": "👍 Лайк"}, {"text": "👎 Дизлайк"}],
            [{"text": "✉️ Повідомлення"}],
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


def end_chat_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Закінчити чат"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def city_keyboard() -> Dict[str, Any]:
    rows = []
    for i in range(0, len(CITIES), 2):
        pair = CITIES[i:i + 2]
        rows.append([{"text": city} for city in pair])
    return {
        "keyboard": rows,
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }


def search_gender_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "Шукаю Чоловіка"}, {"text": "Шукаю Жінку"}],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def search_age_keyboard() -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "14-18"}, {"text": "18-25"}],
            [{"text": "25-40"}, {"text": "40-60"}],
            [{"text": "60+"}],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def search_region_keyboard(my_region: str) -> Dict[str, Any]:
    return {
        "keyboard": [
            [{"text": f"Твій регіон ({my_region})"}],
            [{"text": "Уся Україна"}],
            [{"text": "Назад до меню"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }

