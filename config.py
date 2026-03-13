import os

# Підтримуються обидва імені: BOT_TOKEN (Railway) та TELEGRAM_BOT_TOKEN (legacy)
API_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError(
        "Вкажіть BOT_TOKEN або TELEGRAM_BOT_TOKEN у змінних оточення "
        "(у Railway: Variables → Name: BOT_TOKEN, Value: ваш_токен)"
    )

API_URL = f"https://api.telegram.org/bot{API_TOKEN}/"

