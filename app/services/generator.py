import os
import sys

# Projekt-Wurzelverzeichnis zum Pfad hinzufuegen / Добавление корня проекта в системный путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from app.services.retriever import search_documents

# Antwort basierend auf Kontext und Verlauf generieren / Генерация ответа на основе контекста и истории
def generate_answer(query: str, chat_history: list = None) -> str:
    # Dokumente ueber hybride Suche abrufen / Получение документов через гибридный поиск
    docs = search_documents(query, top_k=3)
    if not docs:
        return "В документах нет этой информации."

    context = "\n\n".join([doc.page_content for doc in docs])

    # Dialogverlauf formatieren / Форматирование истории диалога
    history_text = ""
    if chat_history:
        for msg in chat_history:
            role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "user")
            content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
            sender = "Пользователь" if role == "user" else "Ассистент"
            history_text += f"{sender}: {content}\n"
    else:
        history_text = "Начало диалога."

    # Prompt-Vorlage fuer das Modell / Шаблон промпта для языковой модели
    prompt = PromptTemplate(
        template="""Ты профессиональный технический эксперт и ментор по Python. 
Отвечай на вопросы пользователя, основываясь ТОЛЬКО на предоставленном контексте из базы знаний.

ПРАВИЛА:
1. Если ответа нет в контексте, отвечай строго: "В документах нет этой информации".
2. Пиши кратко, структурно, используй примеры кода при необходимости.
3. Не придумывай факты от себя.

История диалога:
{history}

Контекст:
{context}

Вопрос: {question}
Ответ:""",
        input_variables=["history", "context", "question"]
    )

    # Lokales Sprachmodell initialisieren / Инициализация локальной языковой модели
    llm = OllamaLLM(model="llama3.2")
    chain = prompt | llm

    return chain.invoke({"history": history_text, "context": context, "question": query})

# Testblock / Блок тестирования
if __name__ == "__main__":
    test_question = "What are boolean values and conditionals?"
    answer = generate_answer(test_question)
    print("Antwort / Ответ:\n", answer)
# Zusammenfassung fuer ein bestimmtes Thema erstellen / Генерация краткого резюме по теме
def summarize_topic(topic: str) -> str:
    # Relevante Dokumente ueber Hybridsuche abrufen / Получение релевантных документов
    docs = search_documents(topic, top_k=4)
    if not docs:
        return "Не удалось найти материалы по указанной теме для суммаризации."

    context = "\n\n".join([doc.page_content for doc in docs])

    # Prompt-Vorlage fuer strukturierte Zusammenfassung / Промпт для структурированного резюме
    prompt = PromptTemplate(
        template="""Ты ведущий технический аналитик. 
Составь четкое, структурированное резюме (Executive Summary) по теме: "{topic}".

Базируйся ТОЛЬКО на следующем контексте:
{context}

ФОРМАТ ОТВЕТА:
- **Ключевая суть**: 1-2 предложения.
- **Основные тезисы**: 3-4 маркированных пункта с главными деталями.
- **Практическое применение**: 1 предложение.

Резюме:""",
        input_variables=["topic", "context"]
    )

    llm = OllamaLLM(model="llama3.2")
    chain = prompt | llm

    return chain.invoke({"topic": topic, "context": context})