"""
rebuild_index.py

Run this ONLY when

- New PDFs are added
- PDFs are deleted
- Chunk size changes
- Embedding model changes
"""

import shutil

from chunking import create_chunks
from config import VECTOR_DB_DIR
from logger import get_logger
from vector_store import VectorStoreManager

logger = get_logger(__name__)


def rebuild():

    if VECTOR_DB_DIR.exists():

        logger.info("Deleting old vector database...")

        shutil.rmtree(VECTOR_DB_DIR)

    chunks = create_chunks()

    manager = VectorStoreManager()

    manager.create(chunks)

    logger.info("Index rebuilt successfully.")


if __name__ == "__main__":

    rebuild()