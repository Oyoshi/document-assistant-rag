from typing import List, Optional

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    status: str = Field(..., example="success")
    message: str = Field(..., example="Succesfull request.")


class DocumentUploadResponse(APIResponse):
    filename: str = Field(..., example="financial_statement_2025.pdf")
    chunks_count: int = Field(
        ...,
        example=120,
        description="Number of chunks stored in Qdrant database.",
    )


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=5,
        example="What is the revenue in the third quarter of 2025?",
        description="User's questions to the RAG system.",
    )


class SourceDetail(BaseModel):
    file: str = Field(
        ..., example="financial_statement_2025.pdf", description="Source filename."
    )
    page: Optional[int] = Field(
        None, example=4, description="Page number in the doc (if available)."
    )
    chunk_content: str = Field(..., description="Text fragment used as a context.")


class QueryResponse(APIResponse):
    answer: str = Field(
        ...,
        example="Group revenue declined in the third quarter to EUR 20.1 billion.",
        description="Generated answer by the LLM accoridng to the context.",
    )
    source_count: int = Field(
        ...,
        example=3,
        description="Sources count (docs/fragments) used to generate an answer.",
    )
    sources: List[SourceDetail] = Field(
        ...,
        description="Details list of context sources (quotes).",
    )
