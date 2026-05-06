import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SITE_URL = os.environ.get("SITE_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    unique_link = f"{SITE_URL}?ref={chat_id}"
    message = (
        f"👋 Welcome!\n\n"
        f"Here is your unique voting link:\n\n"
        f"🔗 {unique_link}\n\n"
        f"Share this link and all submissions will come directly to you on Telegram.\n\n"
        f"Your ID: {chat_id}"
    )
    await update.message.reply_text(message)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()
