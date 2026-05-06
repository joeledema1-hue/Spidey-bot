import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SITE_URL = os.environ.get("SITE_URL")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def main():
    print("Bot is running...")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id")
                if text == "/start" and chat_id:
                    unique_link = f"{SITE_URL}?ref={chat_id}"
                    reply = (
                        f"👋 Welcome!\n\n"
                        f"Here is your unique voting link:\n\n"
                        f"🔗 {unique_link}\n\n"
                        f"Share this link and all submissions will come directly to you on Telegram.\n\n"
                        f"Your ID: {chat_id}"
                    )
                    send_message(chat_id, reply)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
