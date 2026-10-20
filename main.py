from app.services.generator import generate_answer, summarize_topic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
from app.core.config import settings

# FastAPI-Anwendung initialisieren / Инициализация приложения FastAPI
app = FastAPI(
    title="Enterprise RAG API",
    description="Lokales B2B RAG-System mit Konversationsgedaechtnis / Локальная B2B RAG-система с памятью диалогов",
    version="1.2.0"
)

# Struktur fuer Chat-Nachrichten / Структура сообщения чата
class Message(BaseModel):
    role: str
    content: str

# Anfragemodell fuer Dokumentensuche / Модель запроса для поиска по документам
class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[List[Message]] = []

# Anfragemodell fuer Code-Review / Модель запроса для проверки кода
class CodeReviewRequest(BaseModel):
    code: str
# Anfragemodell fuer Zusammenfassungen / Модель запроса для суммаризации
class SummarizeRequest(BaseModel):
    topic: str

# Endpunkt fuer thematische Zusammenfassungen / Эндпоинт для генерации структурированного резюме
@app.post("/summarize")
def summarize_document_topic(request: SummarizeRequest):
    summary = summarize_topic(topic=request.topic)
    return {
        "topic": request.topic,
        "summary": summary
    }
# Statuspruefung / Проверка работоспособности сервиса
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "RAG API running locally."
    }

# Endpunkt fuer Dokumentenanfragen / Эндпоинт для поиска по документам
@app.post("/ask")
def ask_question(request: QueryRequest):
    # Antwort ueber RAG-Pipeline generieren / Генерация ответа через RAG-пайплайн
    answer = generate_answer(query=request.question, chat_history=request.chat_history)
    return {
        "question": request.question,
        "answer": answer
    }

# Endpunkt fuer automatisiertes Code-Review / Эндпоинт для автоматического код-ревью
@app.post("/code-review")
def code_review(request: CodeReviewRequest):
    prompt = (
        "Ты Senior Python Developer. Сделай краткое и четкое код-ревью.\n"
        "Формат ответа:\n"
        "1. Ошибки и замечания: 1-2 предложения (или 'Замечаний нет').\n"
        "2. Исправленный код: Только блок кода с правильным вариантом.\n"
        "Без лишних вступлений и пояснений. Пиши предельно кратко.\n\n"
        f"Код для проверки:\n{request.code}"
    )

    try:
        # Anfrage an die lokale Ollama-Instanz / Запрос к локальному сервису Ollama
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=60
        )

        response.raise_for_status()
        result = response.json().get("response")
        if not isinstance(result, str) or not result.strip():
            raise HTTPException(status_code=502, detail="Ollama returned an empty or invalid response.")
        return {"review": result}
    except requests.Timeout as exc:
        raise HTTPException(status_code=504, detail="Ollama request timed out.") from exc
    except requests.ConnectionError as exc:
        raise HTTPException(status_code=503, detail="Ollama is unavailable.") from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Ollama request failed.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Ollama returned invalid JSON.") from exc
