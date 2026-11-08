"""
vector_store.py

Creates or loads the Chroma Vector Database.

If the vector database does not exist,
it is automatically created from the PDFs.
"""

from langchain_chroma import Chroma

from config import (
    VECTOR_DB_DIR,
    COLLECTION_NAME,
    AUTO_CREATE_VECTOR_DB,
)

from embed import EmbeddingModel
from chunking import create_chunks
from ingest import load_documents
from logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:

    def __init__(self):

        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

        self.embedding_model = EmbeddingModel().get_model()

    # ---------------------------------------------------------

    def database_exists(self):

        return (VECTOR_DB_DIR / "chroma.sqlite3").exists()

    # ---------------------------------------------------------

    def create(self, chunks):

        logger.info("=" * 70)
        logger.info("Creating Chroma Vector Database")
        logger.info("=" * 70)

        db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory=str(VECTOR_DB_DIR),
            collection_name=COLLECTION_NAME,
        )

        logger.info("Vector Database Created Successfully.")

        return db

    # ---------------------------------------------------------

    def load(self):

        if self.database_exists():

            logger.info("Loading Existing Vector Database...")

            return Chroma(
                persist_directory=str(VECTOR_DB_DIR),
                embedding_function=self.embedding_model,
                collection_name=COLLECTION_NAME,
            )

        logger.info("Vector Database Not Found.")

        if not AUTO_CREATE_VECTOR_DB:
            raise FileNotFoundError(
                f"Vector database not found at {VECTOR_DB_DIR}. "
                "Download it first (download_database) or enable "
                "AUTO_CREATE_VECTOR_DB for local rebuilds."
            )

        logger.info("Building New Vector Database...")

        documents = load_documents()

        chunks = create_chunks(documents)

        return self.create(chunks)