from typing import Optional, Dict, Any

from handlers import handle_update
from telegram_api import get_updates


def main() -> None:
    print("Bot is running...")
    offset: Optional[int] = None

    while True:
        updates = get_updates(offset)
        results = updates.get("result", []) if isinstance(updates, Dict) else []
        for update in results:
            offset = update["update_id"] + 1
            handle_update(update)


if __name__ == "__main__":
    main()

