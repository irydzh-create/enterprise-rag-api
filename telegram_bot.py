"""Telegram interface with bounded, chat-scoped conversation memory."""
import asyncio
import logging
import os
import time
from collections import OrderedDict

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import SimpleEventIsolation
from dotenv import load_dotenv

from app.core.config import settings

logger = logging.getLogger(__name__)
dp = Dispatcher(events_isolation=SimpleEventIsolation())
user_histories = OrderedDict()
HISTORY_TTL = 3600
MAX_HISTORIES = 1000


def history_key(message):
    return (message.chat.id, message.from_user.id)


def read_history(key):
    now = time.monotonic()
    for old_key, (updated, _) in list(user_histories.items()):
        if now - updated > HISTORY_TTL:
            del user_histories[old_key]
    item = user_histories.get(key)
    return list(item[1]) if item else []


def write_history(key, history):
    user_histories[key] = (time.monotonic(), history[-4:])
    user_histories.move_to_end(key)
    while len(user_histories) > MAX_HISTORIES:
        user_histories.popitem(last=False)


async def api_request(endpoint, payload, field):
    async with httpx.AsyncClient(timeout=httpx.Timeout(300, connect=10)) as client:
        response = await client.post(f"{settings.API_BASE_URL}/{endpoint}", json=payload)
    response.raise_for_status()
    data = response.json()
    answer = data.get(field) if isinstance(data, dict) else None
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("API returned an invalid answer.")
    return answer


async def send_answer(status, message, text):
    # Telegram text messages have a 4096 UTF-16-code-unit limit.
    parts, current, units = [], [], 0
    for char in text:
        size = len(char.encode("utf-16-le")) // 2
        if units + size > 4000:
            parts.append("".join(current))
            current, units = [], 0
        current.append(char)
        units += size
    if current:
        parts.append("".join(current))
    await status.edit_text(parts[0])
    for part in parts[1:]:
        await message.answer(part)


async def perform_request(message, endpoint, payload, field):
    status = await message.answer("Обрабатываю запрос…")
    try:
        answer = await api_request(endpoint, payload, field)
    except (httpx.HTTPError, ValueError):
        logger.exception("API request failed")
        await status.edit_text("Не удалось получить ответ. Проверьте API и Ollama, затем повторите запрос.")
        return None
    await send_answer(status, message, answer)
    return answer


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if message.from_user:
        user_histories.pop(history_key(message), None)
    await message.answer(
        "Задайте вопрос по документам.\n"
        "/review <код> — проверка кода\n"
        "/summary <тема> — краткое резюме\n"
        "/start — очистить историю"
    )


@dp.message(Command("review", "summary"))
async def cmd_tool(message: types.Message):
    command, _, body = message.text.partition(" ")
    body = body.strip()
    name = command.split("@", 1)[0].lstrip("/")
    if not body:
        await message.answer(f"Добавьте текст после /{name}.")
        return
    if name == "review":
        await perform_request(message, "code-review", {"code": body}, "review")
    else:
        await perform_request(message, "summarize", {"topic": body}, "summary")


@dp.message(F.text)
async def handle_document_query(message: types.Message):
    if not message.from_user:
        return
    if message.text.startswith("/"):
        await message.answer("Неизвестная команда. Доступны /start, /review и /summary.")
        return
    key = history_key(message)
    history = read_history(key)
    answer = await perform_request(
        message, "ask", {"question": message.text, "chat_history": history}, "answer"
    )
    if answer is not None:
        write_history(key, history + [
            {"role": "user", "content": message.text},
            {"role": "assistant", "content": answer[:8000]},
        ])


@dp.message()
async def unsupported_message(message: types.Message):
    await message.answer("Пожалуйста, отправьте текстовый вопрос.")


async def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Set TELEGRAM_BOT_TOKEN in .env.")
    async with Bot(token=token) as bot:
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
