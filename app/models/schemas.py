"""
Pydantic schemas for request/response validation.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── FAQ ───────────────────────────────────────────────────────────────────────

class FAQItem(BaseModel):
    """Represents a single FAQ entry as stored in the data source."""

    id: str
    question: str
    answer: str
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ── Chat request / response ───────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Payload sent by the client to the /chat endpoint."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The user's question (1–500 characters).",
        examples=["How do I reset my password?"],
    )

    @field_validator("question", mode="before")
    @classmethod
    def strip_whitespace(cls, v: Any) -> str:
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("question must not be empty or whitespace-only.")
        return v


class ChatResponse(BaseModel):
    """Response returned by the /chat endpoint."""

    question: str = Field(..., description="The original question submitted by the user.")
    answer: str = Field(..., description="The answer to the user's question.")
    matched_faq_id: Optional[str] = Field(
        None,
        description="ID of the matched FAQ entry, or null if no match was found.",
    )
    similarity_score: Optional[float] = Field(
        None,
        description="Cosine similarity score of the best match [0.0 – 1.0], or null if no match.",
    )
    matched: bool = Field(
        ...,
        description="True when a FAQ match was found above the similarity threshold.",
    )


# ── Generic API response wrapper ──────────────────────────────────────────────

class SuccessResponse(BaseModel):
    """Generic wrapper for successful list/detail responses."""

    success: bool = True
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Generic error response shape."""

    success: bool = False
    error: str
    detail: Optional[str] = None


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response from the /health endpoint."""

    status: str = "ok"
    service: str
    version: str
    model_loaded: bool
    faq_count: int
