import os

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from logic.document_loader import load_and_split_document, setup_upload_dir
from logic.logging_config import setup_logging
from logic.models import (
    APIResponse,
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
    SourceDetail,
)
from logic.rag_chain import setup_rag_chain
from logic.vector_store import (
    delete_collection,
    get_qdrant_client,
    store_documents_in_qdrant,
)

# App setup part
logger = setup_logging(__name__)
upload_dir = setup_upload_dir()
rag_chain, retriever = setup_rag_chain()

app = FastAPI(
    title="Document Assistant RAG API",
    description="API to generate responses using RAG on uploaded pdf docs.",
    version="0.1.0",
)


@app.get("/", response_model=APIResponse)
def read_root():
    logger.info("Root")

    return APIResponse(status="success", message="Service is active.")


@app.get("/health", response_model=APIResponse)
def health_check():
    logger.debug("Health check: Verifying Qdrant connection")
    try:
        client = get_qdrant_client()
        client.get_collections()
        return APIResponse(status="success", message="Service and Qdrant are active.")
    except Exception as e:
        logger.error(
            f"Health check failed: Qdrant service is unavailable {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qdrant service is currently unavailable or unreachable.",
        )


@app.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        logger.warning(f"File {file.filename} has not valid extension (*.pdf)")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    file_path = upload_dir / file.filename
    count = 0

    try:
        logger.info(f"Saving a file: {file.filename} to {file_path}")
        with open(file_path, "wb") as buffer:
            # Async read if files are big
            while content := await file.read(1024 * 1024):
                buffer.write(content)
        chunks = load_and_split_document(str(file_path))
        count = store_documents_in_qdrant(chunks)
        logger.info(f"Succesfully proceed {file.filename} and stored {count} vectors")

    except RuntimeError as e:
        # Error thrown by our own implementation from methods above
        logger.error(
            f"Critical error while uploading and processing file {file.filename}: {e}",
            exc_info=True,
        )
        # remove uploaded file in case of error
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"File {file.filename} removed due to processing error")
        detail_msg = f"Processing error: {e.args[0]}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail_msg
        )

    except Exception as e:
        # General error handling like (I/O errors, Qdrant db connection malfunction etc)
        logger.error(
            f"Critical error while uploading and processing file {file.filename}: {e}",
            exc_info=True,
        )
        # remove uploaded file in case of error
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"File {file.filename} removed due to processing error")
        detail_msg = f"Unexpected error while uploading processing the file: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail_msg
        )

    return DocumentUploadResponse(
        status="success",
        message=f"Document proceed and {count} chunks are stored in Qdrant database.",
        filename=file.filename,
        chunks_count=count,
    )


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if rag_chain is None:
        logger.error(
            "RAG chain has not been initialized correctly on startup - Qdrant or Gemini connection failed",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service is currently unavailable. Check Qdrant and Gemini connections.",
        )
    logger.info(f"RAG request received: {request.query[:50]}...")

    try:
        response = rag_chain.invoke(request.query)
        sources_list = []
        for doc in response.get("context", []):
            metadata = doc.metadata
            file_name = metadata.get("source", "N/A").split("/")[-1]
            page_number = metadata.get("page", None)
            sources_list.append(
                SourceDetail(
                    file=file_name,
                    page=page_number if isinstance(page_number, int) else None,
                    chunk_content=doc.page_content,
                )
            )
        source_count = len(sources_list)
        logger.info(f"Generated answer successfully - Used {source_count} sources")

        return QueryResponse(
            status="success",
            message="RAG query processed successfully.",
            answer=response["answer"],
            source_count=source_count,
            sources=sources_list,
        )

    except Exception as e:
        logger.error(
            f"Error while processing RAG query for '{request.query[:50]}...': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during RAG response generation: {e}",
        )


@app.delete("/documents", response_model=APIResponse)
def delete_all_documents():
    logger.warning("Received request to DELETE ALL DOCUMENTS (reset Qdrant collection)")
    try:
        success = delete_collection()
        if success:
            return APIResponse(
                status="success",
                message="All documents deleted. Qdrant collection successfully reset.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Collection deletion failed for unknown reason",
            )

    except RuntimeError as e:
        logger.error(f"Failed to reset database: {e.args[0]}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset error: {e}",
        )
