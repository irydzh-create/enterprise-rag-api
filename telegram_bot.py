import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv

# Загружаем секреты из локального файла .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(" Ошибка: TELEGRAM_BOT_TOKEN не найден в файле .env! Проверьте файл.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Локальная память для хранения истории диалогов каждого пользователя
user_histories = {}


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer(
        "Привет! Я ваш личный AI-ассистент.\n"
        "• Задайте мне вопрос по документам.\n"
        "• Или отправьте код на проверку командной: `/review ваш_код`",
        parse_mode="Markdown"
    )


# НОВЫЙ ОБРАБОТЧИК ДЛЯ КОД-РЕВЬЮ (/review)
@dp.message(Command("review"))
async def cmd_review(message: types.Message):
    # Получаем текст после команды /review (например: /review print(1))
    code_text = message.text.replace("/review", "").strip()

    if not code_text:
        await message.answer(
            " Пожалуйста, укажите код после команды.\n"
            "Пример:\n`/review def add(a, b): return a + b`",
            parse_mode="Markdown"
        )
        return

    processing_msg = await message.answer(" Анализирую ваш код в роли Senior-разработчика...")
    api_url = "http://127.0.0.1:8000/code-review"

    try:
        # Отправляем код на новый эндпоинт FastAPI
        response = requests.post(api_url, json={"code": code_text})

        if response.status_code == 200:
            result_data = response.json()
            ai_answer = result_data.get("review", "Пустой ответ от модели.")
            await processing_msg.edit_text(ai_answer)
        else:
            await processing_msg.edit_text(" Ошибка сервера при проверке кода.")

    except Exception as e:
        await processing_msg.edit_text(f" Ошибка соединения с сервером.\nДетали: {e}")


# СТАНДАРТНЫЙ ОБРАБОТЧИК ДЛЯ ПОИСКА ПО ДОКУМЕНТАМ (RAG)
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    processing_msg = await message.answer("Ищу в документах...")
    api_url = "http://127.0.0.1:8000/ask"

    payload = {
        "question": user_text,
        "chat_history": user_histories[user_id]
    }

    try:
        response = requests.post(api_url, json=payload).json()
        ai_answer = response.get("answer", "Не удалось получить ответ.")

        user_histories[user_id].append({"role": "user", "content": user_text})
        user_histories[user_id].append({"role": "assistant", "content": ai_answer})
        user_histories[user_id] = user_histories[user_id][-4:]

        await processing_msg.edit_text(ai_answer)

    except Exception as e:
        await processing_msg.edit_text(f" Ошибка соединения с сервером RAG.\nДетали: {e}")


async def main():
    print("Telegram-бот успешно запущен! Жду сообщений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())