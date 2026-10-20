from unittest.mock import Mock, patch
from langchain_core.documents import Document
from app.services.generator import generate_answer, summarize_topic


@patch("app.services.generator.search_documents")
@patch("app.services.generator.get_llm")
def test_followup_rewrites_query_before_retrieval(llm_factory, search):
    llm = llm_factory.return_value
    llm.invoke.side_effect = ["Какие недостатки у Python?", "Ответ из документов"]
    search.return_value = [Document(page_content="Python details")]
    answer = generate_answer("Какие у него недостатки?", [
        {"role": "user", "content": "Расскажи про Python"},
    ])
    search.assert_called_once_with("Какие недостатки у Python?", top_k=3)
    assert answer == "Ответ из документов"


@patch("app.services.generator.search_documents", return_value=[])
@patch("app.services.generator.get_llm")
def test_missing_documents_do_not_generate_answer(llm, search):
    assert generate_answer("Unknown") == "В документах нет этой информации."
    llm.return_value.invoke.assert_not_called()


@patch("app.services.generator.search_documents")
@patch("app.services.generator.get_llm")
def test_blank_rewrite_falls_back_to_original(llm, search):
    llm.return_value.invoke.return_value = " "
    search.return_value = []
    generate_answer("Python?", [{"role": "user", "content": "Hi"}])
    search.assert_called_once_with("Python?", top_k=3)
