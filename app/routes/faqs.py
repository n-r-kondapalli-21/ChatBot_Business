"""GET /faqs — list all available FAQ entries."""

from fastapi import APIRouter, Request
from app.models.schemas import FAQItem, SuccessResponse
from typing import List

router = APIRouter(tags=["FAQs"])


@router.get(
    "/faqs",
    response_model=SuccessResponse,
    summary="List all FAQs",
    description="Returns the complete list of FAQ entries currently loaded in the service.",
)
async def list_faqs(request: Request) -> SuccessResponse:
    faqs: List[FAQItem] = request.app.state.faq_loader.get_all()
    return SuccessResponse(
        data=[faq.model_dump() for faq in faqs],
        message=f"{len(faqs)} FAQ entries available.",
    )
