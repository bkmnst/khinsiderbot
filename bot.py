import logging
import os
import khinsider
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import mimetypes
from telegram import Update, InputMediaAudio
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id, text="Please, send a khinsider album ID."
    )


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    album_id = update.message.text
    download_directory = f"./{user_id}/"
    await context.bot.send_message(chat_id=chat_id, text="Starting download...")
    try:
        khinsider.download(
            album_id,
            path=download_directory,
            makeDirs=True,
            formatOrder=None,
            verbose=True,
        )
        await context.bot.send_message(
            chat_id=chat_id, text="Download finished! Uploading files..."
        )
    except khinsider.NonexistentSoundtrackError:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Soundtrack '{album_id}' doesn't exist.",
        )

    mp3_files_list = []
    max_files_per_group = 10
    downloaded_files = os.listdir(download_directory)
    downloaded_files.sort()

    for filename in downloaded_files:
        if filename.endswith(".mp3"):
            mp3_files_list.append(os.path.join(download_directory, filename))
        if filename.endswith(".jpg") or filename.endswith(".png"):
            cover_filename = os.path.join(download_directory, filename)

    if "cover_filename" in locals():
        mime_type, _ = mimetypes.guess_type(cover_filename)
        for mp3_file in mp3_files_list:
            audio = MP3(mp3_file, ID3=ID3)

            with open(cover_filename, "rb") as img:
                audio.tags.add(APIC(mime=mime_type, type=3, data=img.read()))
            audio.save()

    groups = [
        mp3_files_list[i : i + max_files_per_group]
        for i in range(0, len(mp3_files_list), max_files_per_group)
    ]

    for group in groups:
        media_list = []
        for filename in group:
            media_instance = InputMediaAudio(media=open(filename, "rb"))
            media_list.append(media_instance)
        await context.bot.send_media_group(chat_id=chat_id, media=media_list)
    await context.bot.send_message(chat_id=chat_id, text="Done!")
    os.system(f"rm -rf {download_directory}")


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    download_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download)

    application.add_handler(start_handler)
    application.add_handler(download_handler)

    application.run_polling()
