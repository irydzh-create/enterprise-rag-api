import asyncio
import os
import httpx
from app.core.config import settings
from aiogram import Bot, Dispatcher, types, F
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
    api_url = f"{settings.API_BASE_URL}/code-review"

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(api_url, json={"code": code_text})
        if response.status_code == 200:
            review_text = response.json().get("review", "Leere Antwort erhalten.")
            await status_msg.edit_text(review_text[:4096])
        else:
            await status_msg.edit_text("Serverfehler bei der Code-Pruefung.")
    except Exception as e:
        await status_msg.edit_text(f"Verbindungsfehler zum API-Server: {e}")

# Handler fuer allgemeine Dokumentenabfragen / Обработчик вопросов по базе знаний (RAG)
@dp.message(F.text)
async def handle_document_query(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    status_msg = await message.answer("Suche in Dokumenten...")
    api_url = f"{settings.API_BASE_URL}/ask"

    payload = {
        "question": user_text,
        "chat_history": user_histories[user_id]
    }

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            api_response = await client.post(api_url, json=payload)
        api_response.raise_for_status()
        response = api_response.json()
        ai_answer = response.get("answer", "Keine Antwort erhalten.")

        # Verlauf aktualisieren / Обновление истории диалога
        user_histories[user_id].append({"role": "user", "content": user_text})
        user_histories[user_id].append({"role": "assistant", "content": ai_answer})
        user_histories[user_id] = user_histories[user_id][-4:]

        await status_msg.edit_text(ai_answer[:4096])
    except Exception as e:
        await status_msg.edit_text(f"Fehler bei der Verbindung zum RAG-Server: {e}")

# Hauptfunktion fuer Bot-Start / Главная функция запуска бота
async def main():
    print("Telegram-Bot gestartet / Telegram-бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())