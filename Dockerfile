FROM python:3.11

WORKDIR /app

ADD khinsider.py .
ADD bot.py .

RUN pip install beautifulsoup4 requests python-telegram-bot mutagen eyed3 python-dotenv

CMD ["python", "./bot.py"] 