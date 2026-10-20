import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telegram_bot import history_key, user_histories, read_history, write_history, send_answer


def test_history_is_scoped_to_chat_and_user():
    user_histories.clear()
    a = SimpleNamespace(chat=SimpleNamespace(id=1), from_user=SimpleNamespace(id=7))
    b = SimpleNamespace(chat=SimpleNamespace(id=2), from_user=SimpleNamespace(id=7))
    write_history(history_key(a), [{"role": "user", "content": "private"}])
    assert read_history(history_key(b)) == []
    assert read_history(history_key(a))[0]["content"] == "private"


def test_long_unicode_answer_is_not_truncated():
    status, message = AsyncMock(), AsyncMock()
    text = "😀" * 5000
    asyncio.run(send_answer(status, message, text))
    chunks = [status.edit_text.call_args.args[0]] + [
        call.args[0] for call in message.answer.call_args_list
    ]
    assert "".join(chunks) == text
    assert all(len(chunk.encode("utf-16-le")) // 2 <= 4000 for chunk in chunks)
