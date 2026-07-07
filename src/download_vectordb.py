import os
import zipfile
import requests

from config import VECTOR_DB_DIR
from logger import get_logger

logger = get_logger(__name__)

# Replace with your direct download URL later
VECTOR_DB_URL = "https://drive.google.com/file/d/1QVur0lzolEfiY7X2gypSL044vb_DIAfd/view?usp=sharing"


def download_database():

    if (VECTOR_DB_DIR / "chroma.sqlite3").exists():
        logger.info("Vector database already exists.")
        return

    logger.info("Downloading Vector Database...")

    zip_path = "vectordb.zip"

    response = requests.get(VECTOR_DB_URL, stream=True)

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    logger.info("Extracting Vector Database...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall()

    os.remove(zip_path)

    logger.info("Vector Database Ready.")