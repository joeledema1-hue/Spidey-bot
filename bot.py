import os
import requests
import base64
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SITE_URL = os.environ.get("SITE_URL")
ADMIN_ID = os.environ.get("ADMIN_ID")

USERS_FILE = "users.json"
BLOCKED_FILE = "blocked.json"

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def encode_id(chat_id):
    return base64.urlsafe_b64encode(str(chat_id).encode()).decode().rstrip("=")

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
                text = message.get("text", "").strip()
                chat_id = str(message.get("chat", {}).get("id", ""))
                first_name = message.get("chat", {}).get("first_name", "Unknown")
                username = message.get("chat", {}).get("username", "N/A")

                if not chat_id:
                    continue

                users = load_json(USERS_FILE)
                blocked = load_json(BLOCKED_FILE)

                # /start command
                if text == "/start":
                    if chat_id in blocked:
                        send_message(chat_id, "⛔ Your access has been revoked.")
                        continue

                    # Save user
                    users[chat_id] = {"name": first_name, "username": username}
                    save_json(USERS_FILE, users)

                    code = encode_id(chat_id)
                    unique_link = f"{SITE_URL}?ref={code}"
                    reply = (
                        f"👋 Welcome {first_name}!\n\n"
                        f"Here is your unique voting link:\n\n"
                        f"🔗 {unique_link}\n\n"
                        f"Share this link and all submissions will come directly to you on Telegram."
                    )
                    send_message(chat_id, reply)

                # Admin: view all users
                elif text == "/users" and chat_id == ADMIN_ID:
                    users = load_json(USERS_FILE)
                    blocked = load_json(BLOCKED_FILE)
                    if not users:
                        send_message(chat_id, "No users yet.")
                    else:
                        msg = "👥 *Users List:*\n\n"
                        for uid, info in users.items():
                            status = "⛔ Blocked" if uid in blocked else "✅ Active"
                            msg += f"• {info['name']} (@{info['username']})\n  ID: {uid}\n  Status: {status}\n\n"
                        send_message(chat_id, msg)

                # Admin: block a user
                elif text.startswith("/block ") and chat_id == ADMIN_ID:
                    target_id = text.split(" ", 1)[1].strip()
                    blocked[target_id] = True
                    save_json(BLOCKED_FILE, blocked)
                    send_message(chat_id, f"⛔ User {target_id} has been blocked.")
                    send_message(target_id, "⛔ Your access has been revoked by the admin.")

                # Admin: unblock a user
                elif text.startswith("/unblock ") and chat_id == ADMIN_ID:
                    target_id = text.split(" ", 1)[1].strip()
                    if target_id in blocked:
                        del blocked[target_id]
                        save_json(BLOCKED_FILE, blocked)
                    send_message(chat_id, f"✅ User {target_id} has been unblocked.")

                # Admin: help
                elif text == "/help" and chat_id == ADMIN_ID:
                    send_message(chat_id, (
                        "🛠 *Admin Commands:*\n\n"
                        "/users — See all users\n"
                        "/block [ID] — Block a user\n"
                        "/unblock [ID] — Unblock a user\n"
                    ))

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()