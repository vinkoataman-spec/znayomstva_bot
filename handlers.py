import os
from typing import Any, Dict

from keyboards import (
    CITIES,
    buy_premium_keyboard,
    city_keyboard,
    edit_profile_keyboard,
    likes_menu_keyboard,
    main_menu_keyboard,
    gender_keyboard,
    profile_actions_keyboard,
    search_age_keyboard,
    search_gender_keyboard,
    search_region_keyboard,
    search_actions_keyboard,
    subscription_keyboard,
    end_chat_keyboard,
)
from storage import (
    admin_state,
    add_like,
    clear_search_filters,
    ensure_user,
    get_all_complete_users,
    get_likes_received,
    get_saved_search_filters,
    get_user,
    is_profile_complete,
    has_premium,
    premium_expiry,
    save_search_filters,
    set_premium,
    can_use_free_like,
    register_free_like,
    search_state,
    states,
    update_user_fields,
)
from telegram_api import send_message, send_photo, send_sticker


MONO_JAR_URL = os.getenv("MONO_JAR_URL", "https://send.monobank.ua/jar/PASTE_YOUR_JAR_LINK")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0") or "0")

# Optional sticker IDs (Telegram file_id). If not set, stickers are simply skipped.
STICKER_WELCOME = os.getenv("STICKER_WELCOME")
STICKER_PROFILE_SAVED = os.getenv("STICKER_PROFILE_SAVED")
STICKER_LIKE = os.getenv("STICKER_LIKE")
STICKER_PREMIUM = os.getenv("STICKER_PREMIUM")
STICKER_MESSAGE = os.getenv("STICKER_MESSAGE")


def start_registration(chat_id: int) -> None:
    states[chat_id] = "CHOOSING_GENDER"
    if STICKER_WELCOME:
        send_sticker(chat_id, STICKER_WELCOME)
    send_message(chat_id, "✨ Оберіть вашу стать:", reply_markup=gender_keyboard())


def handle_registration_step(message: Dict[str, Any]) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    profile = ensure_user(chat_id)
    state = states.get(chat_id)

    if state == "CHOOSING_GENDER":
        if text in ("Чоловік", "Жінка"):
            update_user_fields(chat_id, gender=text)
            states[chat_id] = "ENTERING_NAME"
            send_message(chat_id, "Вкажіть ваше імʼя:")
        else:
            send_message(
                chat_id,
                "Будь ласка, оберіть одну з кнопок: «Чоловік» або «Жінка».",
                reply_markup=gender_keyboard(),
            )

    elif state == "ENTERING_NAME":
        if text:
            update_user_fields(chat_id, name=text.strip())
            states[chat_id] = "ENTERING_AGE"
            send_message(chat_id, "Вкажіть ваш вік (числом):")
        else:
            send_message(chat_id, "Будь ласка, напишіть імʼя текстом.")

    elif state == "ENTERING_AGE":
        if text.isdigit() and 14 <= int(text) <= 100:
            update_user_fields(chat_id, age=int(text))
            states[chat_id] = "SENDING_PHOTO"
            send_message(
                chat_id,
                "Будь ласка, надішліть вашу фотографію одним фото (не як файл).",
            )
        else:
            send_message(
                chat_id,
                "Вік має бути числом від 14 до 100. Спробуйте ще раз:",
            )

    elif state == "SENDING_PHOTO":
        photos = message.get("photo")
        if photos:
            best_photo = photos[-1]
            update_user_fields(chat_id, photo_file_id=best_photo["file_id"])
            states[chat_id] = "CHOOSING_CITY"
            send_message(
                chat_id,
                "🏙 Оберіть ваше місто/область:",
                reply_markup=city_keyboard(),
            )
        else:
            send_message(
                chat_id,
                "Не бачу фото. Надішліть, будь ласка, фотографію ще раз.",
            )

    elif state == "CHOOSING_CITY":
        if text in CITIES:
            update_user_fields(chat_id, city=text)
            states[chat_id] = "REGISTERED"
            if chat_id not in admin_state:
                admin_state[chat_id] = {}

            if STICKER_PROFILE_SAVED:
                send_sticker(chat_id, STICKER_PROFILE_SAVED)
            send_message(
                chat_id,
                "✅ Ваша анкета збережена!\n"
                "Стать, імʼя, вік, фото та місто записані. 💖",
            )
            send_welcome_after_registration(chat_id)
        else:
            send_message(
                chat_id,
                "Будь ласка, оберіть місто/область кнопками нижче.",
                reply_markup=city_keyboard(),
            )


def send_welcome_after_registration(chat_id: int) -> None:
    text = (
        "💘 Ласкаво просимо в бот для знайомств!\n"
        "Тут ти можеш знайти собі другу половинку.\n\n"
        "✨ Основні можливості:\n"
        "• «Пошук» — перегляд анкет інших людей.\n"
        "• «Мій профіль» — перегляд і редагування своєї анкети.\n"
        "• «Лайки» — хто тебе лайкнув (доступно тільки з преміумом).\n"
        "• «Підписка» — перегляд тарифів та оформлення преміуму.\n"
        "• «Допомога» — звʼязок з адміністратором.\n\n"
        "🆓 Без підписки:\n"
        "• до 20 лайків або дизлайків на тиждень;\n"
        "• повідомлення іншим користувачам недоступні;\n"
        "• розділ «Лайки» недоступний.\n\n"
        "⭐ З підпискою:\n"
        "• безлімітні лайки та дизлайки;\n"
        "• можна писати іншим користувачам;\n"
        "• доступний розділ «Хто мене лайкнув».\n\n"
        "Оформити преміум можна в розділі «Підписка». ⏳"
    )
    send_message(chat_id, text, reply_markup=main_menu_keyboard())


def show_profile(chat_id: int) -> None:
    if not is_profile_complete(chat_id):
        send_message(
            chat_id,
            "ℹ️ У вас ще немає заповненої анкети.\n"
            "Натисніть /start, щоб створити її.",
        )
        return

    profile = get_user(chat_id) or {}
    caption = (
        f"📋 Ваша анкета:\n"
        f"Стать: {profile['gender']}\n"
        f"Імʼя: {profile['name']}\n"
        f"Вік: {profile['age']}\n"
        f"Місто/область: {profile['city']}"
    )

    photo_id = profile.get("photo_file_id")
    if photo_id:
        send_photo(
            chat_id,
            photo_id,
            caption=caption,
            reply_markup=profile_actions_keyboard(),
        )
    else:
        send_message(chat_id, caption, reply_markup=profile_actions_keyboard())


def start_edit_profile(chat_id: int) -> None:
    states[chat_id] = "EDITING_PROFILE_CHOICE"
    send_message(
        chat_id, "Що ви хочете змінити?", reply_markup=edit_profile_keyboard()
    )


def handle_edit_profile(message: Dict[str, Any]) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    state = states.get(chat_id)
    ensure_user(chat_id)

    if state == "EDITING_PROFILE_CHOICE":
        if text == "Змінити імʼя":
            states[chat_id] = "EDITING_NAME"
            send_message(chat_id, "Напишіть нове імʼя:")
        elif text == "Змінити фото":
            states[chat_id] = "EDITING_PHOTO"
            send_message(chat_id, "Надішліть нову фотографію:")
        elif text in ("🔁 Змінити фільтри пошуку", "Змінити фільтри пошуку"):
            clear_search_filters(chat_id)
            states[chat_id] = "CHOOSING_SEARCH_GENDER"
            send_message(
                chat_id,
                "🔎 Налаштуйте фільтри пошуку знову.\n"
                "Етап 1/3: Оберіть, яку стать ви шукаєте:",
                reply_markup=search_gender_keyboard(),
            )
        elif text == "Назад до меню":
            states[chat_id] = "REGISTERED"
            send_message(
                chat_id,
                "Повертаю в меню.",
                reply_markup=main_menu_keyboard(),
            )
        else:
            send_message(chat_id, "Будь ласка, оберіть одну з кнопок.")

    elif state == "EDITING_NAME":
        if text:
            update_user_fields(chat_id, name=text.strip())
            states[chat_id] = "REGISTERED"
            send_message(
                chat_id,
                "Імʼя оновлено.",
                reply_markup=main_menu_keyboard(),
            )
        else:
            send_message(chat_id, "Напишіть імʼя текстом.")

    elif state == "EDITING_PHOTO":
        photos = message.get("photo")
        if photos:
            best_photo = photos[-1]
            update_user_fields(chat_id, photo_file_id=best_photo["file_id"])
            states[chat_id] = "REGISTERED"
            send_message(
                chat_id,
                "Фото оновлено.",
                reply_markup=main_menu_keyboard(),
            )
        else:
            send_message(chat_id, "Не бачу фото. Спробуйте ще раз.")


def start_search(chat_id: int) -> None:
    if not is_profile_complete(chat_id):
        send_message(
            chat_id,
            "⚠️ Спочатку заповніть анкету через /start,\n"
            "щоб інші могли вас бачити.",
        )
        return

    saved = get_saved_search_filters(chat_id)
    if saved:
        begin_search_browsing(
            chat_id,
            saved["wanted_gender"],
            saved["age_range"],
            saved["region_mode"],
            persist=False,
        )
        return

    states[chat_id] = "CHOOSING_SEARCH_GENDER"
    send_message(
        chat_id,
        "🔎 Етап 1/3: Оберіть, яку стать ви шукаєте:",
        reply_markup=search_gender_keyboard(),
    )


def start_filtered_search(chat_id: int, wanted_gender: str) -> None:
    # stage 2 begins after gender selection
    if chat_id not in search_state:
        search_state[chat_id] = {}
    search_state[chat_id]["wanted_gender"] = wanted_gender
    states[chat_id] = "CHOOSING_SEARCH_AGE"
    send_message(
        chat_id,
        "🔎 Етап 2/3: Оберіть вік, який вас цікавить:",
        reply_markup=search_age_keyboard(),
    )


def age_in_range(age: int, age_range: str) -> bool:
    if age_range == "14-18":
        return 14 <= age <= 18
    if age_range == "18-25":
        return 18 <= age <= 25
    if age_range == "25-40":
        return 25 <= age <= 40
    if age_range == "40-60":
        return 40 <= age <= 60
    if age_range == "60+":
        return age >= 60
    return False


def start_filtered_search_with_age(chat_id: int, age_range: str) -> None:
    wanted_gender = search_state.get(chat_id, {}).get("wanted_gender")
    if wanted_gender not in ("Чоловік", "Жінка"):
        states[chat_id] = "CHOOSING_SEARCH_GENDER"
        send_message(
            chat_id,
            "Оберіть стать для пошуку.",
            reply_markup=search_gender_keyboard(),
        )
        return

    search_state[chat_id]["wanted_age_range"] = age_range
    states[chat_id] = "CHOOSING_SEARCH_REGION"
    my_region = (get_user(chat_id) or {}).get("city", "Ваш регіон")
    send_message(
        chat_id,
        f"🔎 Етап 3/3: Оберіть регіон пошуку.\n"
        f"Ваш регіон: {my_region}",
        reply_markup=search_region_keyboard(str(my_region)),
    )


def begin_search_browsing(
    chat_id: int,
    wanted_gender: str,
    age_range: str,
    region_mode: str,
    *,
    persist: bool,
) -> None:
    my_region = (get_user(chat_id) or {}).get("city")
    users_map = get_all_complete_users()

    if wanted_gender not in ("Чоловік", "Жінка") or not isinstance(age_range, str):
        states[chat_id] = "REGISTERED"
        search_state.pop(chat_id, None)
        send_message(
            chat_id,
            "Фільтри пошуку збились. Спробуйте ще раз.",
            reply_markup=main_menu_keyboard(),
        )
        return

    if persist:
        save_search_filters(chat_id, wanted_gender, age_range, region_mode)

    candidates = [
        uid
        for uid in users_map.keys()
        if uid != chat_id
        and users_map.get(uid, {}).get("gender") == wanted_gender
        and age_in_range(int(users_map.get(uid, {}).get("age", 0)), age_range)
        and (
            region_mode == "all"
            or users_map.get(uid, {}).get("city") == my_region
        )
    ]
    if not candidates:
        send_message(
            chat_id,
            "😔 За обраними фільтрами поки що немає анкет.",
            reply_markup=main_menu_keyboard(),
        )
        states[chat_id] = "REGISTERED"
        search_state.pop(chat_id, None)
        return

    search_state[chat_id] = {
        "candidates": candidates,
        "index": 0,
        "wanted_gender": wanted_gender,
        "wanted_age_range": age_range,
        "wanted_region_mode": region_mode,
    }
    states[chat_id] = "SEARCHING"
    show_current_candidate(chat_id)


def start_filtered_search_with_region(chat_id: int, region_mode: str) -> None:
    wanted_gender = search_state.get(chat_id, {}).get("wanted_gender")
    age_range = search_state.get(chat_id, {}).get("wanted_age_range")
    begin_search_browsing(
        chat_id,
        wanted_gender,
        age_range,
        region_mode,
        persist=True,
    )


def show_current_candidate(chat_id: int) -> None:
    state = search_state.get(chat_id)
    if not state:
        send_message(
            chat_id,
            "Немає більше анкет.",
            reply_markup=main_menu_keyboard(),
        )
        states[chat_id] = "REGISTERED"
        return

    candidates = state.get("candidates", [])
    index = state.get("index", 0)
    if index >= len(candidates):
        send_message(
            chat_id,
            "Ви переглянули всі доступні анкети.",
            reply_markup=main_menu_keyboard(),
        )
        states[chat_id] = "REGISTERED"
        return

    target_id = candidates[index]
    profile = get_user(target_id)
    if not profile:
        search_state[chat_id]["index"] += 1
        show_current_candidate(chat_id)
        return

    caption = (
        f"Анкета користувача:\n"
        f"Стать: {profile['gender']}\n"
        f"Імʼя: {profile['name']}\n"
        f"Вік: {profile['age']}\n"
        f"Місто/область: {profile['city']}"
    )

    photo_id = profile.get("photo_file_id")
    if photo_id:
        send_photo(
            chat_id,
            photo_id,
            caption=caption,
            reply_markup=search_actions_keyboard(),
        )
    else:
        send_message(
            chat_id,
            caption,
            reply_markup=search_actions_keyboard(),
        )


def handle_search_actions(message: Dict[str, Any]) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    state = search_state.get(chat_id)

    if not state:
        send_message(
            chat_id,
            "ℹ️ Пошук не активний. Натисніть «Пошук» у меню.",
            reply_markup=main_menu_keyboard(),
        )
        states[chat_id] = "REGISTERED"
        return

    candidates = state.get("candidates", [])
    index = state.get("index", 0)

    if index >= len(candidates):
        send_message(
            chat_id,
            "✅ Немає більше анкет.",
            reply_markup=main_menu_keyboard(),
        )
        states[chat_id] = "REGISTERED"
        return

    target_id = candidates[index]

    if text in ("Лайк", "👍 Лайк"):
        if not has_premium(chat_id):
            if not can_use_free_like(chat_id):
                send_message(
                    chat_id,
                    "Ви використали всі 20 лайків/дизлайків на цей тиждень.\n"
                    "Щоб продовжити ставити оцінки без обмежень, оформіть преміум. ⭐",
                    reply_markup=buy_premium_keyboard(),
                )
                return
            register_free_like(chat_id)

        add_like(chat_id, target_id)
        if STICKER_LIKE:
            send_sticker(chat_id, STICKER_LIKE)
        send_message(chat_id, "💜 Ви поставили лайк цій анкеті.")
        search_state[chat_id]["index"] += 1
        show_current_candidate(chat_id)

    elif text in ("Дизлайк", "👎 Дизлайк", "Наступний"):
        if text != "Наступний" and not has_premium(chat_id):
            if not can_use_free_like(chat_id):
                send_message(
                    chat_id,
                    "Ви використали всі 20 лайків/дизлайків на цей тиждень.\n"
                    "Щоб продовжити ставити оцінки без обмежень, оформіть преміум. ⭐",
                    reply_markup=buy_premium_keyboard(),
                )
                return
            register_free_like(chat_id)
        search_state[chat_id]["index"] += 1
        show_current_candidate(chat_id)

    elif text in ("✉️ Повідомлення", "Повідомлення"):
        if not has_premium(chat_id):
            send_message(
                chat_id,
                "Надсилати повідомлення можуть лише користувачі з преміум-підпискою.",
                reply_markup=buy_premium_keyboard(),
            )
            return
        # зберігаємо, кому пишемо
        if chat_id not in search_state:
            search_state[chat_id] = {}
        search_state[chat_id]["message_target"] = target_id
        states[chat_id] = "SENDING_MESSAGE_TO_USER"
        if STICKER_MESSAGE:
            send_sticker(chat_id, STICKER_MESSAGE)
        send_message(
            chat_id,
            "✉️ Напишіть повідомлення для цього користувача.\n"
            "Воно буде надіслане йому в боті.\n\n"
            "Натисніть «Закінчити чат», щоб повернутися до перегляду анкет.",
            reply_markup=end_chat_keyboard(),
        )

    elif text == "Вийти з пошуку":
        states[chat_id] = "REGISTERED"
        search_state.pop(chat_id, None)
        send_message(
            chat_id,
            "Вихід з пошуку.",
            reply_markup=main_menu_keyboard(),
        )

    else:
        send_message(
            chat_id,
            "Скористайтеся кнопками під анкетою.",
            reply_markup=search_actions_keyboard(),
        )


def handle_likes_section(chat_id: int) -> None:
    if not has_premium(chat_id):
        exp = premium_expiry(chat_id)
        if exp:
            text = (
                "⏱ Ваша преміум-підписка закінчилась.\n"
                "Щоб знову бачити, хто вас лайкнув, оформіть нову підписку. ⭐"
            )
        else:
            text = (
                "У вас немає доступу до цієї функції, "
                "оскільки у вас не підключена преміум-підписка."
            )
        send_message(
            chat_id,
            text,
            reply_markup=buy_premium_keyboard(),
        )
        return

    user_likes = get_likes_received(chat_id)
    count = len(user_likes)
    if count == 0:
        send_message(
            chat_id,
            "Поки що ніхто вас не лайкнув. 😌",
            reply_markup=main_menu_keyboard(),
        )
        return

    send_message(
        chat_id,
        f"Кількість людей, які вас лайкнули: {count}.",
        reply_markup=likes_menu_keyboard(),
    )


def show_who_liked_me(chat_id: int) -> None:
    user_likes = get_likes_received(chat_id)
    if not user_likes:
        send_message(
            chat_id,
            "Немає лайків для показу. 🙂",
            reply_markup=main_menu_keyboard(),
        )
        return

    for liker_id in user_likes:
        profile = get_user(liker_id)
        if not profile:
            continue
        caption = (
            f"❤️ Той, хто вас лайкнув:\n"
            f"Стать: {profile['gender']}\n"
            f"Імʼя: {profile['name']}\n"
            f"Вік: {profile['age']}\n"
            f"Місто/область: {profile['city']}"
        )
        photo_id = profile.get("photo_file_id")
        if photo_id:
            send_photo(chat_id, photo_id, caption=caption)
        else:
            send_message(chat_id, caption)

    send_message(
        chat_id,
        "Це всі, хто вас лайкнув. 💌",
        reply_markup=main_menu_keyboard(),
    )


def handle_subscription(chat_id: int) -> None:
    states[chat_id] = "CHOOSING_SUBSCRIPTION"
    text = (
        "⭐ Оберіть тариф підписки:\n\n"
        "• 🗓️ Тиждень — 100 грн\n"
        "• 📅 Місяць — 400 грн\n\n"
        "Після вибору тарифу я надішлю посилання на банку для оплати."
    )
    send_message(chat_id, text, reply_markup=subscription_keyboard())


def send_subscription_payment_info(chat_id: int, period: str, amount_uah: int) -> None:
    text = (
        f"✅ Обрано: {period}\n"
        f"💳 Сума: {amount_uah} грн\n\n"
        f"🔗 Посилання на банку:\n{MONO_JAR_URL}\n\n"
        "❗ ОБОВ'ЯЗКОВО в коментарі до платежу прикріпіть ваш нік в Telegram.\n"
        "Наприклад: @your_username"
    )
    send_message(chat_id, text, reply_markup=main_menu_keyboard())


def notify_admin_purchase_intent(chat_id: int, period: str, amount_uah: int, user: Any) -> None:
    if ADMIN_CHAT_ID <= 0:
        return
    username = user.get("username") if isinstance(user, dict) else None
    first_name = user.get("first_name") if isinstance(user, dict) else None
    last_name = user.get("last_name") if isinstance(user, dict) else None

    nick = f"@{username}" if isinstance(username, str) and username else "(no username)"
    full_name = " ".join([p for p in [first_name, last_name] if isinstance(p, str) and p]).strip()
    if not full_name:
        full_name = "(no name)"

    text = (
        "🧾 Запит на преміум\n\n"
        f"User ID: {chat_id}\n"
        f"Name: {full_name}\n"
        f"Nick: {nick}\n"
        f"Тариф: {period}\n"
        f"Сума: {amount_uah} грн\n\n"
        "Щоб видати преміум:\n"
        f"/premium_week {chat_id}\n"
        f"/premium_month {chat_id}"
    )
    send_message(ADMIN_CHAT_ID, text)


def grant_premium(chat_id: int) -> None:
    # legacy button: grants 30 days
    set_premium(chat_id, 30)
    if STICKER_PREMIUM:
        send_sticker(chat_id, STICKER_PREMIUM)
    send_message(
        chat_id,
        "🎉 Преміум-підписка активована!\n"
        "Тепер доступний розділ «Лайки».",
        reply_markup=main_menu_keyboard(),
    )


def is_admin(chat_id: int) -> bool:
    return ADMIN_CHAT_ID > 0 and chat_id == ADMIN_CHAT_ID


def handle_admin_commands(message: Dict[str, Any]) -> bool:
    chat_id = message["chat"]["id"]
    if not is_admin(chat_id):
        return False

    text = message.get("text", "").strip()

    # Grant commands
    if text.startswith("/premium_week"):
        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            send_message(chat_id, "Формат: /premium_week <user_id>")
            return True
        target_id = int(parts[1])
        expiry = set_premium(target_id, 7)
        send_message(chat_id, f"✅ Видано преміум на 7 днів для {target_id}. До: {expiry}")
        send_message(target_id, "🎉 Вам видано преміум на 7 днів! ⭐")
        return True

    if text.startswith("/premium_month"):
        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            send_message(chat_id, "Формат: /premium_month <user_id>")
            return True
        target_id = int(parts[1])
        expiry = set_premium(target_id, 30)
        send_message(chat_id, f"✅ Видано преміум на 30 днів для {target_id}. До: {expiry}")
        send_message(target_id, "🎉 Вам видано преміум на 30 днів! ⭐")
        return True

    if text == "/admin":
        send_message(
            chat_id,
            "Адмін-команди:\n"
            "/premium_week <user_id>\n"
            "/premium_month <user_id>",
        )
        return True

    return False


def handle_help(chat_id: int) -> None:
    states[chat_id] = "ASKING_HELP"
    text = (
        "✉️ Напишіть, будь ласка, ваше запитання або опишіть проблему.\n"
        "Адміністратор отримає це повідомлення і відповість вам у боті."
    )
    send_message(chat_id, text, reply_markup=end_chat_keyboard())


def handle_update(update: Dict[str, Any]) -> None:
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user = message.get("from", {})

    if handle_admin_commands(message):
        return

    if text.startswith("/start"):
        ensure_user(chat_id)
        start_registration(chat_id)
        return

    state = states.get(chat_id)

    if state in {
        "CHOOSING_GENDER",
        "ENTERING_NAME",
        "ENTERING_AGE",
        "SENDING_PHOTO",
        "CHOOSING_CITY",
    }:
        handle_registration_step(message)
        return

    if state in {"EDITING_PROFILE_CHOICE", "EDITING_NAME", "EDITING_PHOTO"}:
        handle_edit_profile(message)
        return

    if state == "SEARCHING":
        handle_search_actions(message)
        return

    if state == "CHOOSING_SEARCH_GENDER":
        if text == "Шукаю Чоловіка":
            start_filtered_search(chat_id, "Чоловік")
            return
        if text == "Шукаю Жінку":
            start_filtered_search(chat_id, "Жінка")
            return
        if text == "Назад до меню":
            states[chat_id] = "REGISTERED"
            send_message(chat_id, "Повертаю в головне меню.", reply_markup=main_menu_keyboard())
            return
        send_message(
            chat_id,
            "Оберіть стать кнопками нижче.",
            reply_markup=search_gender_keyboard(),
        )
        return

    if state == "CHOOSING_SEARCH_AGE":
        if text in {"14-18", "18-25", "25-40", "40-60", "60+"}:
            start_filtered_search_with_age(chat_id, text)
            return
        if text == "Назад до меню":
            states[chat_id] = "REGISTERED"
            search_state.pop(chat_id, None)
            send_message(chat_id, "Повертаю в головне меню.", reply_markup=main_menu_keyboard())
            return
        send_message(
            chat_id,
            "Оберіть діапазон віку кнопками нижче.",
            reply_markup=search_age_keyboard(),
        )
        return

    if state == "CHOOSING_SEARCH_REGION":
        my_region = (get_user(chat_id) or {}).get("city", "Ваш регіон")
        my_region_btn = f"Твій регіон ({my_region})"
        if text == my_region_btn:
            start_filtered_search_with_region(chat_id, "my")
            return
        if text == "Уся Україна":
            start_filtered_search_with_region(chat_id, "all")
            return
        if text == "Назад до меню":
            states[chat_id] = "REGISTERED"
            search_state.pop(chat_id, None)
            send_message(chat_id, "Повертаю в головне меню.", reply_markup=main_menu_keyboard())
            return
        send_message(
            chat_id,
            "Оберіть регіон кнопками нижче.",
            reply_markup=search_region_keyboard(str(my_region)),
        )
        return

    if state == "ASKING_HELP":
        if text == "Закінчити чат":
            states[chat_id] = "REGISTERED"
            send_message(
                chat_id,
                "Чат з підтримкою завершено.",
                reply_markup=main_menu_keyboard(),
            )
            return
        question = text.strip()
        if not question:
            send_message(
                chat_id,
                "Повідомлення порожнє. Напишіть, будь ласка, текст запитання.",
                reply_markup=end_chat_keyboard(),
            )
            return
        # Відправляємо адміну
        if ADMIN_CHAT_ID > 0:
            username = user.get("username")
            first_name = user.get("first_name")
            last_name = user.get("last_name")
            nick = f"@{username}" if isinstance(username, str) and username else "(no username)"
            full_name = " ".join(
                [p for p in [first_name, last_name] if isinstance(p, str) and p]
            ).strip() or "(no name)"
            admin_text = (
                "🆘 Новий запит у підтримку\n\n"
                f"User ID: {chat_id}\n"
                f"Name: {full_name}\n"
                f"Nick: {nick}\n\n"
                f"Повідомлення:\n{question}"
            )
            send_message(ADMIN_CHAT_ID, admin_text)
        # Відповідь користувачу
        states[chat_id] = "REGISTERED"
        send_message(
            chat_id,
            "✅ Ваше повідомлення відправлено адміністратору.\n"
            "Він відповість вам тут, у боті.",
            reply_markup=main_menu_keyboard(),
        )
        return

    if state == "SENDING_MESSAGE_TO_USER":
        if text == "Закінчити чат":
            states[chat_id] = "SEARCHING"
            if chat_id in search_state and "message_target" in search_state[chat_id]:
                del search_state[chat_id]["message_target"]
            send_message(
                chat_id,
                "Чат завершено. Продовжуємо пошук анкет.",
                reply_markup=search_actions_keyboard(),
            )
            return
        target_id = search_state.get(chat_id, {}).get("message_target")
        text_to_send = message.get("text", "").strip()
        if not target_id:
            states[chat_id] = "REGISTERED"
            send_message(
                chat_id,
                "Не знайдено користувача для повідомлення. Спробуйте знову через пошук.",
                reply_markup=main_menu_keyboard(),
            )
            return
        if not text_to_send:
            send_message(
                chat_id,
                "Повідомлення порожнє. Напишіть текст для користувача.",
            )
            return
        # надсилаємо іншому користувачу
        send_message(
            target_id,
            "📩 Вам надійшло нове повідомлення від іншого користувача бота:\n\n"
            f"{text_to_send}",
        )
        if STICKER_MESSAGE:
            send_sticker(target_id, STICKER_MESSAGE)
        send_message(
            chat_id,
            "✅ Повідомлення надіслано.",
            reply_markup=search_actions_keyboard(),
        )
        # повертаємо в режим пошуку
        states[chat_id] = "SEARCHING"
        if chat_id in search_state and "message_target" in search_state[chat_id]:
            del search_state[chat_id]["message_target"]
        return

    if state == "CHOOSING_SUBSCRIPTION":
        if text in ("🗓️ Підписка на тиждень", "Підписка на тиждень"):
            states[chat_id] = "REGISTERED"
            notify_admin_purchase_intent(chat_id, "Підписка на тиждень", 100, user)
            send_subscription_payment_info(chat_id, "Підписка на тиждень", 100)
            return
        if text in ("📅 Підписка на місяць", "Підписка на місяць"):
            states[chat_id] = "REGISTERED"
            notify_admin_purchase_intent(chat_id, "Підписка на місяць", 400, user)
            send_subscription_payment_info(chat_id, "Підписка на місяць", 400)
            return
        if text == "Назад до меню":
            states[chat_id] = "REGISTERED"
            send_message(chat_id, "Повертаю в головне меню.", reply_markup=main_menu_keyboard())
            return
        send_message(chat_id, "Оберіть тариф кнопками нижче.", reply_markup=subscription_keyboard())
        return

    # Далі — обробка основного меню
    if text in ("🔍 Пошук", "Пошук"):
        start_search(chat_id)
    elif text in ("👤 Мій профіль", "Мій профіль"):
        show_profile(chat_id)
    elif text == "Редагувати мій профіль":
        start_edit_profile(chat_id)
    elif text in ("❤️ Лайки", "Лайки"):
        handle_likes_section(chat_id)
    elif text == "Переглянути, хто мене лайкнув":
        show_who_liked_me(chat_id)
    elif text in ("⭐ Підписка", "Підписка"):
        handle_subscription(chat_id)
    elif text == "Купити преміум":
        # з розділу «Лайки» перекидаємо в «Підписка», без авто-активації
        handle_subscription(chat_id)
    elif text in ("❓ Допомога", "Допомога"):
        handle_help(chat_id)
    elif text == "Назад до меню":
        states[chat_id] = "REGISTERED"
        send_message(
            chat_id,
            "Повертаю в головне меню.",
            reply_markup=main_menu_keyboard(),
        )
    else:
        if is_profile_complete(chat_id):
            send_message(
                chat_id,
                "Не зрозумів команду. Скористайтеся кнопками меню нижче.",
                reply_markup=main_menu_keyboard(),
            )
        else:
            send_message(
                chat_id,
                "Спочатку завершіть заповнення анкети. Натисніть /start, щоб почати.",
            )

