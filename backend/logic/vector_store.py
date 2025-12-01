import os
from typing import List

from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from logic.logging_config import setup_logging
from qdrant_client import QdrantClient

logger = setup_logging(__name__)

QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = os.environ.get("QDRANT_GRPC_PORT", "6334")
COLLECTION_NAME = "rag_documents_collection"

# LangChain automatically read OPENAI_API_KEY via os.environ
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def get_qdrant_client():
    # Używamy portu gRPC (6334)
    return QdrantClient(
        host=QDRANT_HOST, port=int(QDRANT_PORT), prefer_grpc=True, timeout=10
    )


def get_vector_store():
    client = get_qdrant_client()

    vector_store = Qdrant(
        client=client,
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
    )
    return vector_store


def store_documents_in_qdrant(
    chunks: List[Document], collection_name: str = COLLECTION_NAME
):
    if not chunks:
        logger.warning("No chunks which can be stored in Qdrant")
        return 0

    client = get_qdrant_client()

    # Qdrant.from_documents is responsible for 3 things here:
    # 1. Generate vectors via 'embeddings' object
    # 2. Create new collection (or reusing old one if exists - force_recreate is falsy for this reason)
    # 3. Fill vectors and metadata
    Qdrant.from_documents(
        chunks,
        embeddings,
        client=client,
        collection_name=collection_name,
        force_recreate=False,
    )
    return len(chunks)
