"""
Configuration module for the FAQ Chatbot.

All configurable settings are centralised here.
They can be overridden via environment variables or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "FAQ Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── Semantic Matching ─────────────────────────────────────────────────────
    # Lightweight, CPU-friendly sentence-transformer model
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Local cache directory for the model (downloads from Hugging Face on first run)
    cache_folder_path: str = str(
        Path(__file__).resolve().parent.parent / "embedded_model"
    )

    # Minimum cosine-similarity score [0.0 – 1.0] to accept a match.
    # Questions scoring below this threshold get the fallback response.
    # Empirically tuned for all-MiniLM-L6-v2:
    # – weakest true-positive paraphrase scored ~0.40
    # – strongest irrelevant question scored ~0.24
    # A threshold of 0.38 gives a comfortable margin on both sides.
    similarity_threshold: float = 0.38

    # ── Data ─────────────────────────────────────────────────────────────────
    faq_file_path: str = str(
        Path(__file__).resolve().parent.parent / "data" / "faqs.json"
    )

    # ── Fallback ──────────────────────────────────────────────────────────────
    fallback_message: str = (
        "I'm sorry, I don't have an answer to that question right now. "
        "Please contact our support team at support@example.com for further assistance."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Singleton – imported everywhere else in the project
settings = Settings()
