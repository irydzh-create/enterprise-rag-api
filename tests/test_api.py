import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

# TestClient fuer API-Tests initialisieren / Инициализация тестового клиента API
client = TestClient(app)


# Test fuer den Healthcheck-Endpunkt / Тест эндпоинта проверки статуса API
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# Test fuer den Frage-Endpunkt mit Mocking / Тест эндпоинта /ask с мокированием RAG-генератора
@patch("main.generate_answer")
def test_ask_endpoint_success(mock_generate_answer):
    mock_generate_answer.return_value = "Python ist eine interpretierte Programmiersprache."

    payload = {
        "question": "Was ist Python?",
        "chat_history": []
    }
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Was ist Python?"
    assert data["answer"] == "Python ist eine interpretierte Programmiersprache."
    mock_generate_answer.assert_called_once()


# Test fuer Pydantic-Validierungsfehler / Тест валидации Pydantic при отсутствии обязательного поля
def test_ask_endpoint_validation_error():
    # Senden einer leeren Anfrage / Отправка запроса без обязательного поля question
    response = client.post("/ask", json={})
    assert response.status_code == 422


# Test fuer den Code-Review-Endpunkt / Тест эндпоинта /code-review с мокированием Ollama
@patch("main.requests.post")
def test_code_review_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "response": "1. Bemerkung: Keine Fehler.\n2. Code: def add(a: int, b: int) -> int: return a + b"
    }

    payload = {"code": "def add(a, b): return a + b"}
    response = client.post("/code-review", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "review" in data
    assert "Bemerkung" in data["review"]
    mock_post.assert_called_once()


# Test fuer Fehlerbehandlung bei Verbindungsabbruch zu Ollama / Тест обработки сбоя соединения с LLM
@patch("main.requests.post")
def test_code_review_connection_failure(mock_post):
    import requests
    mock_post.side_effect = requests.ConnectionError("Ollama connection refused")

    payload = {"code": "print('hello')"}
    response = client.post("/code-review", json=payload)

    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama is unavailable."
# Test fuer den Zusammenfassungs-Endpunkt / Тест эндпоинта /summarize с мокированием
@patch("main.summarize_topic")
def test_summarize_endpoint_success(mock_summarize):
    mock_summarize.return_value = "- Ключевая суть: Описание темы.\n- Основные тезисы: Пункт 1."

    payload = {"topic": "Variables and Data Types"}
    response = client.post("/summarize", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Variables and Data Types"
    assert "summary" in data
    mock_summarize.assert_called_once()

@patch("main.requests.post")
def test_code_review_timeout(mock_post):
    import requests
    mock_post.side_effect = requests.Timeout()
    assert client.post("/code-review", json={"code": "pass"}).status_code == 504


@patch("main.requests.post")
def test_code_review_upstream_error(mock_post):
    import requests
    mock_post.return_value.raise_for_status.side_effect = requests.HTTPError()
    assert client.post("/code-review", json={"code": "pass"}).status_code == 502


@patch("main.requests.post")
def test_code_review_invalid_json(mock_post):
    mock_post.return_value.json.side_effect = ValueError("Invalid JSON")
    assert client.post("/code-review", json={"code": "pass"}).status_code == 502


@patch("main.requests.post")
def test_code_review_empty_response(mock_post):
    mock_post.return_value.json.return_value = {"response": ""}
    assert client.post("/code-review", json={"code": "pass"}).status_code == 502
