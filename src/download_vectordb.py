"""
download_vectordb.py

Downloads the prebuilt Chroma vector database for Render / cloud deploys.
"""

import os
import zipfile
from pathlib import Path

from config import VECTOR_DB_DIR, PROJECT_ROOT
from logger import get_logger

logger = get_logger(__name__)

VECTOR_DB_FILE_ID = "1QVur0lzolEfiY7X2gypSL044vb_DIAfd"
VECTOR_DB_URL = f"https://drive.google.com/uc?id={VECTOR_DB_FILE_ID}"


def download_database():
    """Download and extract vectordb.zip if chroma.sqlite3 is missing."""

    if (VECTOR_DB_DIR / "chroma.sqlite3").exists():
        logger.info("Vector database already exists.")
        return

    zip_path = PROJECT_ROOT / "vectordb.zip"

    # If vectordb.zip is already present locally, extract directly
    if zip_path.exists() and zip_path.stat().st_size > 1000:
        logger.info("Local vectordb.zip found. Extracting...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(PROJECT_ROOT)
        if (VECTOR_DB_DIR / "chroma.sqlite3").exists():
            logger.info("Vector Database extracted and ready.")
            return

    logger.info("Downloading Vector Database...")

    try:
        try:
            import gdown
            gdown.download(
                VECTOR_DB_URL,
                str(zip_path),
                quiet=False,
            )
        except ImportError:
            logger.info("gdown not installed, downloading via requests...")
            import requests
            response = requests.get(VECTOR_DB_URL, stream=True)
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)

        if not zip_path.exists() or zip_path.stat().st_size < 1000:
            raise RuntimeError(
                "Vector DB download failed or returned an empty file. "
                "Check that the Google Drive link is public."
            )

        logger.info("Extracting Vector Database...")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(PROJECT_ROOT)

        logger.info(f"VECTOR_DB_DIR = {VECTOR_DB_DIR}")
        logger.info(
            f"Vector DB exists? {(VECTOR_DB_DIR / 'chroma.sqlite3').exists()}"
        )

        if VECTOR_DB_DIR.exists():
            logger.info(
                f"Vector DB folder contents: {os.listdir(VECTOR_DB_DIR)}"
            )

        zip_path.unlink(missing_ok=True)

        if not (VECTOR_DB_DIR / "chroma.sqlite3").exists():
            raise FileNotFoundError(
                "Extracted archive but chroma.sqlite3 was not found. "
                "Check the zip layout."
            )

        logger.info("Vector Database Ready.")

    except Exception as e:
        logger.error(f"Failed to download/extract vector database: {e}")
        raise
