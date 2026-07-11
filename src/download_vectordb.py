import os
import zipfile
import requests

from config import VECTOR_DB_DIR
from logger import get_logger

logger = get_logger(__name__)

# Replace with your direct downlo
VECTOR_DB_URL = "https://drive.google.com/uc?export=download&id=1QVur0lzolEfiY7X2gypSL044vb_DIAfd"

def download_database():

    if (VECTOR_DB_DIR / "chroma.sqlite3").exists():
        logger.info("Vector database already exists.")
        return

    logger.info("Downloading Vector Database...")

    zip_path = "vectordb.zip"

    try:
        response = requests.get(VECTOR_DB_URL, stream=True)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info("Extracting Vector Database...")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall()

        # ===== DEBUG =====
        logger.info(f"VECTOR_DB_DIR = {VECTOR_DB_DIR}")
        logger.info(f"Project root contents: {os.listdir('.')}")

        logger.info(
            f"Vector DB exists? {(VECTOR_DB_DIR / 'chroma.sqlite3').exists()}"
        )

        if VECTOR_DB_DIR.exists():
            logger.info(
                f"Vector DB folder contents: {os.listdir(VECTOR_DB_DIR)}"
            )
        # ================

        os.remove(zip_path)

        logger.info("Vector Database Ready.")

    except Exception as e:
        logger.error(f"Failed to download/extract vector database: {e}")
        raise