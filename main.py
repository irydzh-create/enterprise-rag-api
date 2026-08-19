from fastapi import FastAPI
from pydantic import BaseModel
from app.core.config import settings
from app.services.generator import generate_answer

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")


# Создаем строгую схему того, как должен выглядеть запрос от пользователя
class QueryRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "message": "Система RAG работает локально и приватно."
    }


# Создаем точку доступа для вопросов (POST-запрос)
@app.post("/ask")
def ask_question(request: QueryRequest):
    """
    Принимает вопрос от пользователя, ищет ответ в базе данных
    и возвращает сгенерированный результат.
    """
    # Вызываем нашу функцию, которую мы написали на прошлом шаге
    answer = generate_answer(request.question)

    return {
        "question": request.question,
        "answer": answer
    }