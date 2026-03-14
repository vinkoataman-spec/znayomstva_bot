from typing import Any, Dict

from keyboards import (
    buy_premium_keyboard,
    edit_profile_keyboard,
    likes_menu_keyboard,
    main_menu_keyboard,
    gender_keyboard,
    profile_actions_keyboard,
    search_actions_keyboard,
)
from storage import (
    ensure_user,
    is_profile_complete,
    likes_received,
    premium_users,
    search_state,
    states,
    users,
)
from telegram_api import send_message, send_photo


def start_registration(chat_id: int) -> None:
    states[chat_id] = "CHOOSING_GENDER"
    send_message(chat_id, "✨ Оберіть вашу стать:", reply_markup=gender_keyboard())


def handle_registration_step(message: Dict[str, Any]) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    profile = ensure_user(chat_id)
    state = states.get(chat_id)

    if state == "CHOOSING_GENDER":
        if text in ("Чоловік", "Жінка"):
            profile["gender"] = text
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
            profile["name"] = text.strip()
            states[chat_id] = "ENTERING_AGE"
            send_message(chat_id, "Вкажіть ваш вік (числом):")
        else:
            send_message(chat_id, "Будь ласка, напишіть імʼя текстом.")

    elif state == "ENTERING_AGE":
        if text.isdigit() and 16 <= int(text) <= 100:
            profile["age"] = int(text)
            states[chat_id] = "SENDING_PHOTO"
            send_message(
                chat_id,
                "Будь ласка, надішліть вашу фотографію одним фото (не як файл).",
            )
        else:
            send_message(
                chat_id,
                "Вік має бути числом від 16 до 100. Спробуйте ще раз:",
            )

    elif state == "SENDING_PHOTO":
        photos = message.get("photo")
        if photos:
            best_photo = photos[-1]
            profile["photo_file_id"] = best_photo["file_id"]
            states[chat_id] = "REGISTERED"
            likes_received.setdefault(chat_id, [])
            premium_users.setdefault(chat_id, False)

            send_message(
                chat_id,
                "✅ Ваша анкета збережена!\n"
                "Стать, імʼя, вік і фото записані. 💖",
            )
            send_welcome_after_registration(chat_id)
        else:
            send_message(
                chat_id,
                "Не бачу фото. Надішліть, будь ласка, фотографію ще раз.",
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
        "Без преміуму діє обмеження, наприклад, до 25 повідомлень або дій на день. ⏳"
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

    profile = users[chat_id]
    caption = (
        f"📋 Ваша анкета:\n"
        f"Стать: {profile['gender']}\n"
        f"Імʼя: {profile['name']}\n"
        f"Вік: {profile['age']}"
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
    profile = ensure_user(chat_id)

    if state == "EDITING_PROFILE_CHOICE":
        if text == "Змінити імʼя":
            states[chat_id] = "EDITING_NAME"
            send_message(chat_id, "Напишіть нове імʼя:")
        elif text == "Змінити фото":
            states[chat_id] = "EDITING_PHOTO"
            send_message(chat_id, "Надішліть нову фотографію:")
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
            profile["name"] = text.strip()
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
            profile["photo_file_id"] = best_photo["file_id"]
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

    candidates = [
        uid
        for uid in users.keys()
        if uid != chat_id and is_profile_complete(uid)
    ]
    if not candidates:
        send_message(
            chat_id,
            "😔 Поки що немає інших анкет для показу.",
            reply_markup=main_menu_keyboard(),
        )
        return

    search_state[chat_id] = {"candidates": candidates, "index": 0}
    states[chat_id] = "SEARCHING"
    show_current_candidate(chat_id)


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
    profile = users.get(target_id)
    if not profile:
        search_state[chat_id]["index"] += 1
        show_current_candidate(chat_id)
        return

    caption = (
        f"Анкета користувача:\n"
        f"Стать: {profile['gender']}\n"
        f"Імʼя: {profile['name']}\n"
        f"Вік: {profile['age']}"
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

    if text == "Лайк":
        likes_received.setdefault(target_id, [])
        if chat_id not in likes_received[target_id]:
            likes_received[target_id].append(chat_id)
        if LIKE_STICKER_ID:
            send_sticker(chat_id, LIKE_STICKER_ID)
        send_message(chat_id, "Ви поставили лайк цій анкеті.")
        search_state[chat_id]["index"] += 1
        show_current_candidate(chat_id)

    elif text == "Дизлайк" or text == "Наступний":
        search_state[chat_id]["index"] += 1
        show_current_candidate(chat_id)

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
    if not premium_users.get(chat_id):
        send_message(
            chat_id,
            "У вас немає доступу до цієї функції, оскільки у вас не підключена преміум-підписка.",
            reply_markup=buy_premium_keyboard(),
        )
        return

    user_likes = likes_received.get(chat_id, [])
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
    user_likes = likes_received.get(chat_id, [])
    if not user_likes:
        send_message(
            chat_id,
            "Немає лайків для показу. 🙂",
            reply_markup=main_menu_keyboard(),
        )
        return

    for liker_id in user_likes:
        profile = users.get(liker_id)
        if not profile:
            continue
        caption = (
            f"❤️ Той, хто вас лайкнув:\n"
            f"Стать: {profile['gender']}\n"
            f"Імʼя: {profile['name']}\n"
            f"Вік: {profile['age']}"
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
    text = (
        "⭐ Преміум-підписка відкриває додаткові можливості:\n"
        "• Необмежена кількість переглядів анкет і лайків.\n"
        "• Доступ до розділу «Хто мене лайкнув».\n\n"
        "Тарифи (приклад):\n"
        "• 1 місяць — 5$\n"
        "• 3 місяці — 12$\n"
        "• 6 місяців — 20$\n\n"
        "Для тесту тут ми просто дамо вам преміум після натискання «Купити преміум». ✨"
    )
    send_message(chat_id, text, reply_markup=buy_premium_keyboard())


def grant_premium(chat_id: int) -> None:
    premium_users[chat_id] = True
    send_message(
        chat_id,
        "🎉 Преміум-підписка активована!\n"
        "Тепер доступний розділ «Лайки».",
        reply_markup=main_menu_keyboard(),
    )


def handle_help(chat_id: int) -> None:
    text = (
        "Якщо у вас виникли питання або потрібна допомога,\n"
        "напишіть, будь ласка, своє повідомлення тут, і ми його переглянемо."
    )
    send_message(chat_id, text, reply_markup=main_menu_keyboard())


def handle_update(update: Dict[str, Any]) -> None:
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

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
    }:
        handle_registration_step(message)
        return

    if state in {"EDITING_PROFILE_CHOICE", "EDITING_NAME", "EDITING_PHOTO"}:
        handle_edit_profile(message)
        return

    if state == "SEARCHING":
        handle_search_actions(message)
        return

    # Далі — обробка основного меню
    if text == "Пошук":
        start_search(chat_id)
    elif text == "Мій профіль":
        show_profile(chat_id)
    elif text == "Редагувати мій профіль":
        start_edit_profile(chat_id)
    elif text == "Лайки":
        handle_likes_section(chat_id)
    elif text == "Переглянути, хто мене лайкнув":
        show_who_liked_me(chat_id)
    elif text == "Підписка":
        handle_subscription(chat_id)
    elif text == "Купити преміум":
        grant_premium(chat_id)
    elif text == "Допомога":
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

