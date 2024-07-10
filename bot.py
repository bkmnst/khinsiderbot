import logging
import os
import khinsider
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Please, send a khinsider album ID."
    )


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    album_id = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Starting download..."
    )
    try:
        khinsider.download(
            album_id, path="./download", makeDirs=True, formatOrder=None, verbose=True
        )
    except khinsider.NonexistentSoundtrackError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Soundtrack '{album_id}' doesn't exist.",
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    download_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download)

    application.add_handler(start_handler)
    application.add_handler(download_handler)

    application.run_polling()
