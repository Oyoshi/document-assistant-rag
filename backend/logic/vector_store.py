import os
from typing import List

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import Qdrant
from logic.logging_config import setup_logging
from qdrant_client import QdrantClient

logger = setup_logging(__name__)

QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = os.environ.get("QDRANT_GRPC_PORT", "6334")
COLLECTION_NAME = "rag_documents_collection"

# LangChain automatically read GOOGLE_API_KEY via os.environ
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")


def get_qdrant_client():
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
    if not client.collection_exists(collection_name):
        from qdrant_client.http import models

        logger.info(f"Collection '{collection_name}' does not exist. Creating it...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=768, distance=models.Distance.COSINE
            ),
        )

    qdrant = Qdrant(
        client=client,
        embeddings=embeddings,
        collection_name=collection_name,
    )
    qdrant.add_documents(chunks)
    return len(chunks)


def delete_collection(collection_name: str = COLLECTION_NAME) -> bool:
    logger.warning(f"Attempting to delete collection: {collection_name}")
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections

        if collection_name not in collections:
            logger.info(
                f"Collection '{collection_name}' does not exist - skipping deletion"
            )
            return True

        result = client.delete_collection(collection_name=collection_name)
        if result:
            logger.info(f"Collection '{collection_name}' successfully deleted")
            return True
        return False

    except Exception as e:
        logger.error(
            f"Error deleting collection '{collection_name}': {e}", exc_info=True
        )
        raise RuntimeError(f"Failed to delete Qdrant collection: {e}")
