from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from app.services.generator import generate_answer

app = FastAPI(
    title="Enterprise RAG API",
    description="B2B локальная RAG-система с памятью диалогов",
    version="1.1.0"
)


# Новая структура: Сообщение в чате
class Message(BaseModel):
    role: str  # "user" (человек) или "assistant" (нейросеть)
    content: str  # Текст сообщения


# Обновленная структура: Запрос от пользователя
class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[Message]] = []  # История (по умолчанию пустая)


@app.post("/ask")
def ask_question(req: QueryRequest):
    # Превращаем историю в удобный словарь
    history_dicts = [{"role": msg.role, "content": msg.content} for msg in req.chat_history]

    # Передаем вопрос и историю генератору
    answer = generate_answer(req.question, history_dicts)

    return {
        "question": req.question,
        "answer": answer
    }