import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv

# Umgebungsvariablen laden / Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN nicht in .env gefunden / Токен не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Lokaler Speicher fuer Konversationsverlaeufe / Локальное хранилище истории диалогов
user_histories = {}

# Handler fuer den Startbefehl / Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer(
        "AI-Assistent bereit.\n"
        "- Frage zu den Dokumenten stellen (Text eingeben)\n"
        "- Code-Review anfordern: /review <Code>",
        parse_mode="Markdown"
    )

# Handler fuer Code-Review / Обработчик команды /review
@dp.message(Command("review"))
async def cmd_review(message: types.Message):
    code_text = message.text.replace("/review", "").strip()

    if not code_text:
        await message.answer(
            "Bitte Code nach dem Befehl angeben.\nBeispiel: `/review def add(a, b): return a + b`",
            parse_mode="Markdown"
        )
        return

    status_msg = await message.answer("Code-Analyse laeuft...")
    api_url = "http://127.0.0.1:8000/code-review"

    try:
        response = requests.post(api_url, json={"code": code_text}, timeout=180)
        if response.status_code == 200:
            review_text = response.json().get("review", "Leere Antwort erhalten.")
            await status_msg.edit_text(review_text)
        else:
            await status_msg.edit_text("Serverfehler bei der Code-Pruefung.")
    except Exception as e:
        await status_msg.edit_text(f"Verbindungsfehler zum API-Server: {e}")

# Handler fuer allgemeine Dokumentenabfragen / Обработчик вопросов по базе знаний (RAG)
@dp.message()
async def handle_document_query(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    status_msg = await message.answer("Suche in Dokumenten...")
    api_url = "http://127.0.0.1:8000/ask"

    payload = {
        "question": user_text,
        "chat_history": user_histories[user_id]
    }

    try:
        response = requests.post(api_url, json=payload, timeout=60).json()
        ai_answer = response.get("answer", "Keine Antwort erhalten.")

        # Verlauf aktualisieren / Обновление истории диалога
        user_histories[user_id].append({"role": "user", "content": user_text})
        user_histories[user_id].append({"role": "assistant", "content": ai_answer})
        user_histories[user_id] = user_histories[user_id][-4:]

        await status_msg.edit_text(ai_answer)
    except Exception as e:
        await status_msg.edit_text(f"Fehler bei der Verbindung zum RAG-Server: {e}")

# Hauptfunktion fuer Bot-Start / Главная функция запуска бота
async def main():
    print("Telegram-Bot gestartet / Telegram-бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())