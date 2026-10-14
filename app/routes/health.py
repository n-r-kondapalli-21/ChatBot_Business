"""GET /health — liveness & readiness probe."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/",
    summary="API root",
    description="Redirects to the API documentation.",
)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the service status, loaded model flag, and FAQ count.",
)
async def health_check(request: Request) -> HealthResponse:
    state = request.app.state
    return HealthResponse(
        status="ok",
        service=state.settings.app_name,
        version=state.settings.app_version,
        model_loaded=state.model_loaded,
        faq_count=state.faq_loader.count(),
    )
