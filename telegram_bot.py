import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Ошибка: TELEGRAM_BOT_TOKEN не найден в файле .env! Проверьте файл.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_histories = {}
user_langs = {}

# Словари с жестким разделением на 2 функции для всех 4 языков
T = {
    "de": {
        "start": "Hallo! Wählen Sie eine Aktion:\n\n1️⃣ **Dokumentensuche (RAG)**: Schreiben Sie einfach Ihre Frage.\n2️⃣ **Code-Review**: Senden Sie den Code mit dem Befehl `/review`.",
        "no_code": "⚠️ Senden Sie den Code nach dem Befehl. Beispiel:\n`/review print('hello')`",
        "too_short": "⚠️ Die Anfrage ist zu kurz. Bitte beschreiben Sie Ihr Problem genauer."
    },
    "ru": {
        "start": "Привет! Выберите действие:\n\n1️⃣ **Поиск по базе (RAG)**: Просто напишите ваш вопрос.\n2️⃣ **Код-ревью**: Отправьте код с командой `/review`.",
        "no_code": "⚠️ Укажите код после команды. Пример:\n`/review print('hello')`",
        "too_short": "⚠️ Запрос слишком короткий. Опишите вопрос подробнее."
    },
    "en": {
        "start": "Hello! Choose an action:\n\n1️⃣ **Document Search (RAG)**: Just type your question.\n2️⃣ **Code Review**: Send your code with the `/review` command.",
        "no_code": "⚠️ Provide the code after the command. Example:\n`/review print('hello')`",
        "too_short": "⚠️ The query is too short. Please describe your question in more detail."
    },
    "uk": {
        "start": "Привіт! Оберіть дію:\n\n1️⃣ **Пошук по базі (RAG)**: Просто напишіть ваше запитання.\n2️⃣ **Код-рев'ю**: Відправте код з командою `/review`.",
        "no_code": "⚠️ Вкажіть код після команди. Приклад:\n`/review print('hello')`",
        "too_short": "⚠️ Запит занадто короткий. Опишіть запитання детальніше."
    }
}


def get_text(user_id, key):
    # По умолчанию немецкий язык
    lang = user_langs.get(user_id, "de")
    return T.get(lang, T["de"]).get(key, T["de"][key])


def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang_de"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ]
    ])


async def fetch_api(message: types.Message, endpoint: str, payload: dict, response_key: str):
    msg = await message.answer("⏳ ...")
    try:
        resp = requests.post(f"http://127.0.0.1:8000/{endpoint}", json=payload)
        if resp.status_code == 200:
            result = resp.json().get(response_key, "Пустой ответ")
            await msg.edit_text(result)
            return result
        await msg.edit_text(f"❌ API Error ({resp.status_code}): {resp.text[:100]}")
    except Exception as e:
        await msg.edit_text(f"❌ Connection Error: {e}")
    return None


@dp.message(CommandStart())
async def cmd_start(m: types.Message):
    user_histories[m.from_user.id] = []
    await m.answer("Sprache wählen / Choose language / Выберите язык:", reply_markup=get_lang_keyboard())


@dp.callback_query(F.data.startswith("lang_"))
async def process_lang_selection(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    user_langs[user_id] = lang_code

    try:
        # Пытаемся изменить текст (обернуто в try-except для защиты от ошибки двойного клика)
        await callback.message.edit_text(get_text(user_id, "start"), parse_mode="Markdown")
    except Exception:
        pass

    await callback.answer()


# НАПРАВЛЕНИЕ 2: ПОМОЩЬ С КОДОМ
@dp.message(Command("review"))
async def cmd_review(m: types.Message):
    code = m.text.replace("/review", "").strip()
    if not code:
        return await m.answer(get_text(m.from_user.id, "no_code"), parse_mode="Markdown")
    await fetch_api(m, "code-review", {"code": code}, "review")


# НАПРАВЛЕНИЕ 1: РАБОТА С БАЗОЙ ДАННЫХ (ДОКУМЕНТЫ)
@dp.message()
async def handle_message(m: types.Message):
    uid = m.from_user.id

    # Защита от галлюцинаций: блокируем слишком короткие запросы
    if len(m.text) < 5:
        return await m.answer(get_text(uid, "too_short"))

    user_histories.setdefault(uid, [])
    ans = await fetch_api(m, "ask", {"question": m.text, "chat_history": user_histories[uid]}, "answer")

    if ans:
        user_histories[uid].extend([{"role": "user", "content": m.text}, {"role": "assistant", "content": ans}])
        user_histories[uid] = user_histories[uid][-4:]


if __name__ == "__main__":
    print("Telegram-бот запущен. Ожидание сообщений...")
    asyncio.run(dp.start_polling(bot))