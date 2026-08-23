from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from app.services.vector_store import get_vector_store


# # Function to generate an answer based on vector DB and LLM / Функция для генерации ответа на основе векторной БД и LLM
def generate_answer(query: str, chat_history: list = None) -> str:
    # # Get vector store / Получаем векторное хранилище
    vector_store = get_vector_store()
    if not vector_store:
        return "База данных пуста или не найдена. / Database is empty or not found."

    # # Retrieve relevant document chunks / Получаем релевантные куски документов
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    # # Format chat history / Форматируем историю диалога
    history_text = ""
    if chat_history:
        for msg in chat_history:
            sender = "Пользователь" if msg["role"] == "user" else "Ассистент"
            history_text += f"{sender}: {msg['content']}\n"
    else:
        history_text = "Начало диалога. / Start of the conversation."

    # # Define prompt template / Задаем шаблон промпта
    prompt = PromptTemplate(
        template="""Ты профессиональный ментор и эксперт по Python. Отвечай на вопросы пользователя, основываясь ТОЛЬКО на предоставленном контексте из базы знаний.

ПРАВИЛА:
1. Если ответа нет в контексте, отвечай: "В документах нет этой информации".
2. Пиши кратко, структурно, используй примеры кода при необходимости.
3. Не придумывай информацию.

История диалога:
{history}

Контекст:
{context}

Вопрос: {question}
Ответ:""",
        input_variables=["history", "context", "question"]
    )

    # # Initialize Ollama model / Инициализируем модель Ollama
    llm = OllamaLLM(model="llama3.2")

    # # Create chain and invoke / Создаем цепочку и вызываем генерацию
    chain = prompt | llm

    return chain.invoke({"history": history_text, "context": context, "question": query})