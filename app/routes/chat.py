"""POST /chat — submit a question and receive an answer."""

import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.matcher import MatchResult

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a question",
    description=(
        "Submit a natural-language question. "
        "The service uses semantic similarity to find the best matching FAQ and returns its answer. "
        "If no match is found above the configured threshold, a friendly fallback message is returned."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "Validation error – e.g. empty question."},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    matcher = request.app.state.matcher

    try:
        result: MatchResult = matcher.match(payload.question)
    except Exception as exc:  # pragma: no cover
        logger.exception("Unexpected error during matching: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal server error",
                detail="An unexpected error occurred while processing your question.",
            ).model_dump(),
        )

    return ChatResponse(
        question=payload.question,
        answer=result.answer,
        matched_faq_id=result.faq_id,
        similarity_score=result.similarity_score,
        matched=result.matched,
    )
