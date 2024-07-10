import logging
import os
import khinsider
from telegram import Update, InputMediaPhoto, InputMediaAudio
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id, text="Please, send a khinsider album ID."
    )


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    album_id = update.message.text
    download_directory = "./download/"
    await context.bot.send_message(chat_id=chat_id, text="Starting download...")
    try:
        khinsider.download(
            album_id,
            path=download_directory,
            makeDirs=True,
            formatOrder=None,
            verbose=True,
        )
    except khinsider.NonexistentSoundtrackError:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Soundtrack '{album_id}' doesn't exist.",
        )
    await context.bot.send_message(
        chat_id=chat_id, text="Download finished! Uploading files..."
    )

    mp3_files_list = []
    max_files_per_group = 10

    for filename in os.listdir(download_directory):
        if filename.endswith(".mp3"):
            mp3_files_list.append(filename)
    
    groups = [
        mp3_files_list[i : i + max_files_per_group]
        for i in range(0, len(mp3_files_list), max_files_per_group)
    ]

    for group in groups:
        media_list = []
        for filename in group:
            file_path = os.path.join(download_directory, filename)
            media_instance = InputMediaAudio(media=open(file_path, "rb"))
            media_list.append(media_instance)
        await context.bot.send_media_group(chat_id=chat_id, media=media_list)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    media_test = InputMediaPhoto(
        media="https://tinypng.com/backend/opt/download/m7hrqsfg5b0s5vwetq3bgmp8j0b267pz/Screenshot%202024-07-05%20110426.png"
    )
    await context.bot.send_media_group(chat_id=chat_id, media=[media_test] * 10)


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    download_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download)
    test_handler = CommandHandler("test", test)

    application.add_handler(start_handler)
    application.add_handler(download_handler)
    application.add_handler(test_handler)

    application.run_polling()
