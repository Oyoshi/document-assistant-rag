import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logic.logging_config import setup_logging

logger = setup_logging(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_and_split_document(file_path: str) -> List[Document]:
    logger.info(f"Loading document: {file_path}")

    try:
        loader = PyPDFLoader(file_path)
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )

        chunks = text_splitter.split_documents(data)

        logger.info(
            f"Document has been splitted to {len(chunks)} chunks (chunk size: {CHUNK_SIZE}, chunk overlap: {CHUNK_OVERLAP})"
        )
        return chunks
    except Exception as e:
        logger.error(
            f"Error processing PDF file '{os.path.basename(file_path)}': {e}",
            exc_info=True,
        )
        # Throwing the RuntimeError which can be handled at the upper level and returned as HTTP 500
        raise RuntimeError(f"Error processing PDF file: {e}")
