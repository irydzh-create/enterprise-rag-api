import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# 🎯 ВСТАВЬТЕ СЮДА ВАШ ТОКЕН ОТ BOTFATHER
BOT_TOKEN = "8494125951:AAFOTFKL-TL2nAHpsSAzcp2pjWkT8BNsTIU"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Локальная память для хранения истории диалогов каждого пользователя
user_histories = {}


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    # Очищаем историю при команде /start
    user_histories[message.from_user.id] = []
    await message.answer("Привет! Я ваш личный AI-ассистент. Задайте мне вопрос по документам Ирины!")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    # Если пользователь пишет впервые, создаем для него пустую историю
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Отправляем сообщение "Ищу информацию..." (показываем, что бот не завис)
    processing_msg = await message.answer("🤔 Ищу в документах...")

    # Адрес нашего FastAPI сервера
    api_url = "http://127.0.0.1:8000/ask"

    # Упаковываем вопрос и историю (прямо как мы делали в Swagger)
    payload = {
        "question": user_text,
        "chat_history": user_histories[user_id]
    }

    try:
        # Отправляем запрос на наш сервер
        response = requests.post(api_url, json=payload).json()
        ai_answer = response.get("answer", "Не удалось получить ответ.")

        # Обновляем память диалога (сохраняем вопрос и ответ)
        user_histories[user_id].append({"role": "user", "content": user_text})
        user_histories[user_id].append({"role": "assistant", "content": ai_answer})

        # Оставляем только последние 4 сообщения, чтобы не перегружать память
        user_histories[user_id] = user_histories[user_id][-4:]

        # Редактируем сообщение с "Ищу..." на готовый ответ
        await processing_msg.edit_text(ai_answer)

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Ошибка соединения с сервером RAG. Убедитесь, что FastAPI (uvicorn) запущен!\nДетали: {e}")


async def main():
    print("🤖 Telegram-бот успешно запущен! Жду сообщений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())