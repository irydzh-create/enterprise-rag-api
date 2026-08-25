from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import requests
from app.services.generator import generate_answer

# Initialize FastAPI application / Инициализация приложения FastAPI
app = FastAPI(
    title="Enterprise RAG API",
    description="B2B локальная RAG-система с памятью диалогов / B2B local RAG system with chat history",
    version="1.1.0"
)

# Structure for chat history / Структура для истории сообщений
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

# User query model for document search / Запрос от пользователя для поиска по документам
class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[Message]] = []

# Model for accepting code for review / Модель для приема кода на проверку
class CodeReviewRequest(BaseModel):
    code: str

# Endpoint for asking questions / Эндпоинт для вопросов по документам
@app.post("/ask")
def ask_question(request: QueryRequest):
    # ИСПРАВЛЕНО: передаем аргументы позиционно, чтобы избежать конфликта имен параметров
    answer = generate_answer(request.question, request.chat_history)
    return {"answer": answer}

# Endpoint for code review / Эндпоинт для код-ревью
@app.post("/code-review")
def code_review(request: CodeReviewRequest):
    # Form a strict and concise prompt for code review / Формируем строгий и краткий промпт для код-ревью
    # Промпт на английском с жестким требованием отвечать на немецком
    prompt = (
        "You are a Senior Python Developer. Perform a strict and concise code review.\n"
        "IMPORTANT: Write your response entirely in German (Deutsch).\n"
        "Format of your response:\n"
        "1. **Probleme**: 1-2 sentences (or 'Keine Probleme' if code is fine).\n"
        "2. **Korrigierter Code**: Just the code block with the fix.\n"
        "Do not write long introductions. Be extremely concise.\n\n"
        f"Code to review:\n{request.code}"
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1  # Low temperature for strictness / Низкая температура для строгости
            }
        }
    )

    if response.status_code == 200:
        result = response.json().get("response", "Не удалось получить ответ от модели. / Failed to get response.")
        return {"review": result}
    else:
        return {"review": "Ошибка связи с локальной моделью Ollama. / Ollama connection error."}

@app.get("/")
async def root():
    return {"message": "Enterprise RAG API is running!"}