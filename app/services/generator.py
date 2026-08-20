from langchain_ollama import OllamaLLM  # <-- НОВЫЙ ИМПОРТ
from langchain_core.prompts import PromptTemplate
from app.services.vector_store import get_vector_store


def generate_answer(query: str, chat_history: list = None) -> str:
    vector_store = get_vector_store()
    if not vector_store:
        return "К сожалению, база данных пуста или не найдена."

    # 1. Достаем 5 кусков текста из базы
    retriever = vector_store.as_retriever(search_kwargs={"k": 10})
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    # 2. Красиво оформляем историю диалога
    history_text = ""
    if chat_history:
        for msg in chat_history:
            sender = "Пользователь" if msg["role"] == "user" else "Ассистент"
            history_text += f"{sender}: {msg['content']}\n"
    else:
        history_text = "Это начало диалога."

        prompt = PromptTemplate(
            template="""Ты точный AI-аналитик. Твоя задача — отвечать на вопросы по личным карьерным документам Ирины Джеляловой (Iryna Dzhelialova). 
             Учитывай, что если в вопросе говорится "я", "Ирина" или "Iryna", речь идет об одном и том же человеке!

             ВАЖНЫЕ ПРАВИЛА:
             1. Если ответ не найден в контексте, скажи "В документах нет этой информации".
             2. Ничего не выдумывай от себя.
             3. Профессия Ирины: Lehrer für Informatik und Mathematik (Учитель информатики и математики).

             История нашего диалога:
             {history}

             Контекст из документов:
             {context}

             Текущий вопрос пользователя: {question}
             Ответ:""",
            input_variables=["history", "context", "question"]
        )
    print("🧠 Нейросеть анализирует контекст и историю диалога...")

    # Подключаем локальную Ollama через новый класс
    llm = OllamaLLM(model="llama3.2")  # <-- НОВЫЙ КЛАСС

    # Собираем цепочку и генерируем ответ
    chain = prompt | llm
    return chain.invoke({"history": history_text, "context": context, "question": query})