from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from logic.logging_config import setup_logging
from logic.vector_store import get_vector_store

logger = setup_logging(__name__)

RAG_PROMPT_TEMPLATE = """
You are a RAG Documentation Assistant. Your task is to provide accurate and comprehensive answers
based *exclusively* on the context provided below.

If the context does not contain the answer, do not invent information. Respond that the information
is not available in the documents provided.

Context:
---
{context}
---

User question: {question}
"""


def setup_rag_chain():
    logger.info("Starting RAG chain initialization...")

    try:
        vector_store = get_vector_store()
        # Retrieve 3 most similar fragments
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

        rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

        # Building the Answer Chain - this chain takes context (docs) and question, creates the prompt, and generates the answer
        answer_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | rag_prompt
            | llm
            | StrOutputParser()
        )

        # Use RunnableParallel to return both the answer and the sources - required to preserve the context
        rag_chain_with_source = RunnableParallel(answer=answer_chain, context=retriever)
        logger.info("RAG chain with source support successfully built")
        return rag_chain_with_source, retriever

    except Exception as e:
        logger.error(f"Failed to initialize RAG chain: {e}", exc_info=True)
        return None, None
