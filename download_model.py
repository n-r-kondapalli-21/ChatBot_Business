"""
Script to download the sentence-transformer model to the local embedded_model folder.
Run this once to avoid downloading the model on every server startup.
"""

from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings

def main():
    print(f"Downloading model '{settings.embedding_model_name}' to '{settings.cache_folder_path}'...")
    print("This may take a few minutes on the first run (model size: ~90 MB)\n")

    # Create embedded_model directory if it doesn't exist
    embedded_model_dir = Path(settings.cache_folder_path)
    embedded_model_dir.mkdir(parents=True, exist_ok=True)

    # Download the model
    model = SentenceTransformer(
        settings.embedding_model_name,
        cache_folder=settings.cache_folder_path
    )

    print(f"\n[OK] Model downloaded successfully!")
    print(f"[OK] Model cached at: {settings.cache_folder_path}")
    print(f"[OK] Model name: {settings.embedding_model_name}")
    print(f"\nThe server will now use this local cached model on startup.")

if __name__ == "__main__":
    main()
