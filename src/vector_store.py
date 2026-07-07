"""
vector_store.py

Handles creation and loading of the Chroma Vector Database.
"""

from pathlib import Path

from langchain_chroma import Chroma

from config import (
    VECTOR_DB_DIR,
    COLLECTION_NAME,
)
from embed import EmbeddingModel
from logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:

    def __init__(self):

        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

        self.embedding_model = EmbeddingModel().get_model()

    def database_exists(self):

        return (VECTOR_DB_DIR / "chroma.sqlite3").exists()

    def load(self):

        logger.info("Loading existing ChromaDB...")

        return Chroma(
            persist_directory=str(VECTOR_DB_DIR),
            embedding_function=self.embedding_model,
            collection_name=COLLECTION_NAME,
        )

    def create(self, chunks):

        logger.info("Creating new ChromaDB...")

        db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory=str(VECTOR_DB_DIR),
            collection_name=COLLECTION_NAME,
        )

        logger.info("Database created successfully.")

        return db