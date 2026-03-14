# Telegram Dating Bot

A simple Telegram bot for dating. Users register with a profile (gender, name, age, photo), browse other profiles with like/dislike actions, and can upgrade to premium for additional features.

## Features

- **Registration** — Gender → Name → Age → Photo
- **Main menu** — Search, My Profile, Likes, Subscription, Help
- **Search** — Browse other users' profiles with like/dislike actions
- **My Profile** — View and edit your profile (name, photo)
- **Likes** — See who liked you (premium only)
- **Subscription** — Premium plans (currently test mode, no real payment)

> All data is stored in memory. Restarting the bot clears profiles, likes, and states.

## Project Structure

| File | Description |
|------|-------------|
| `main.py` | Entry point, long-polling loop, routes updates to handlers |
| `config.py` | Reads `BOT_TOKEN` from environment, builds `API_URL` |
| `telegram_api.py` | Low-level Telegram API calls (`sendMessage`, `sendPhoto`, `getUpdates`) |
| `keyboards.py` | Reply keyboards (main menu, gender, profile, search, etc.) |
| `storage.py` | In-memory storage (profiles, states, likes, premium status) |
| `handlers.py` | Business logic (registration, search, likes, subscription, help) |
| `requirements.txt` | Python dependencies |

## Requirements

- Python 3.10+
- Telegram bot token (from [@BotFather](https://t.me/BotFather))

## Installation

```bash
pip install -r requirements.txt
```

Or minimally:

```bash
pip install requests
```

## Configuration

### Bot Token

Set the environment variable **`BOT_TOKEN`** (or `TELEGRAM_BOT_TOKEN`) with your bot token from BotFather.

**Railway:**

1. Open your project on [Railway](https://railway.app)
2. Go to **Variables** (or **Settings** → Variables)
3. Add: **Name** = `BOT_TOKEN`, **Value** = your token
4. Save — the service will redeploy with the new token

**Local (Windows PowerShell):**

```powershell
$env:BOT_TOKEN="YOUR_BOT_TOKEN"
python main.py
```

**Local (Linux/macOS):**

```bash
export BOT_TOKEN="YOUR_BOT_TOKEN"
python main.py
```

## Run

```bash
python main.py
```

Then:

1. Find your bot in Telegram
2. Send `/start`
3. Complete registration (gender, name, age, photo)
4. Use the main menu buttons

## Limitations & Notes

- Data is stored in memory only; no persistence across restarts
- Premium is activated by pressing the button (no real payment integration yet)
- For production you would need:
  - A database (PostgreSQL, SQLite)
  - Real payment integration
  - Proper validation, logging, and error handling
