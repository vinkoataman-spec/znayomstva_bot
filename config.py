import os

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable with your bot token")

API_URL = f"https://api.telegram.org/bot{API_TOKEN}/"

