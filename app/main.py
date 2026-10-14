"""
FastAPI application factory and lifespan manager.

Startup sequence
────────────────
1. Load configuration (Settings).
2. Load FAQ data (FAQLoader).
3. Load the sentence-transformer model once.
4. Build the FAQMatcher with pre-computed embeddings.
5. Store everything in app.state so routes can access it without globals.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models.schemas import ErrorResponse
from app.routes import chat, faqs, health
from app.services.faq_loader import FAQLoader
from app.services.matcher import FAQMatcher

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Runs once at startup (before the first request) and once at shutdown.
    All heavy initialisation (model loading, embedding pre-computation) happens here.
    """
    logger.info("═══ FAQ Chatbot API – starting up ═══")

    # 1. Attach settings to app state.
    app.state.settings = settings

    # 2. Load FAQ data.
    faq_loader = FAQLoader(settings.faq_file_path)
    faq_loader.load()
    app.state.faq_loader = faq_loader

    # 3. Load the embedding model (downloaded on first run, cached locally).
    logger.info("Loading embedding model '%s' …", settings.embedding_model_name)
    model = SentenceTransformer(
        settings.embedding_model_name,
        cache_folder=settings.cache_folder_path
    )
    app.state.model_loaded = True
    logger.info("Embedding model loaded successfully.")

    # 4. Build the matcher (pre-computes FAQ embeddings).
    app.state.matcher = FAQMatcher(
        model=model,
        faqs=faq_loader.get_all(),
        similarity_threshold=settings.similarity_threshold,
        fallback_message=settings.fallback_message,
    )

    logger.info("═══ Startup complete — ready to serve requests ═══")
    yield  # ← application runs here

    # Shutdown
    logger.info("═══ FAQ Chatbot API – shutting down ═══")
    app.state.model_loaded = False


# ── Application factory ───────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A standalone FAQ chatbot API that uses semantic search to match "
            "user questions against a predefined FAQ dataset."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS (open for local development; tighten for production) ─────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom exception handlers ─────────────────────────────────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        detail = "; ".join(
            f"{' → '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in errors
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation error",
                detail=detail,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal server error",
                detail=str(exc),
            ).model_dump(),
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(faqs.router)
    app.include_router(chat.router)

    return app


# ── Entrypoint ────────────────────────────────────────────────────────────────
app = create_app()
