from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from app.services.vector_store import get_vector_store

def generate_answer(question: str, chat_history: list) -> str:
    # 1. Поиск по базе данных ChromaDB
    try:
        vector_store = get_vector_store()
        docs = vector_store.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        print(f"Ошибка при поиске в БД: {e}")
        context = ""

    # 2. Формируем историю чата в текст
    history_text = ""
    if chat_history:
        for msg in chat_history:
            role = "User" if msg.role == "user" else "AI"
            history_text += f"{role}: {msg.content}\n"

    # 3. Упрощенный и надежный системный промпт с якорем Answer
    prompt_template = """You are a helpful AI assistant.
Answer the user's question using ONLY the provided context.
If the context is empty or does not contain the answer, you MUST reply with this exact phrase: "Leider gibt es in den Dokumenten keine Informationen dazu." (If the user asks in Russian or Ukrainian, translate this phrase accordingly).
Do NOT repeat the question. Do not make up facts.

Chat History:
{history}

Context from documents:
{context}

User Question:
{question}

Answer:"""

    # 4. Собираем промпт
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["history", "context", "question"]
    )

    # 5. Инициализируем модель Ollama (с низкой температурой для точности)
    llm = OllamaLLM(model="llama3.2", temperature=0.1)

    # 6. Создаем цепочку и вызываем генерацию
    chain = prompt | llm

    return chain.invoke({"history": history_text, "context": context, "question": question})