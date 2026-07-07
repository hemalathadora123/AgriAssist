"""
embed.py

Loads embedding model and prepares documents for vector storage.

Project : AgriAssist
"""

from typing import List, Tuple

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from chunking import create_chunks
from config import EMBEDDING_MODEL, DEVICE
from logger import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    """
    Wrapper around HuggingFace embedding model.
    """

    def __init__(self):

        logger.info("=" * 60)
        logger.info("Loading Embedding Model")
        logger.info("=" * 60)

        self.model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": DEVICE
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        logger.info(f"Embedding Model : {EMBEDDING_MODEL}")

    def get_model(self):

        return self.model


def prepare_embeddings() -> Tuple[
    HuggingFaceEmbeddings,
    List[Document]
]:
    """
    Returns embedding model and chunked documents.
    """

    chunks = create_chunks()

    if not chunks:

        logger.warning("No chunks found.")

        return None, []

    embedding_model = EmbeddingModel().get_model()

    logger.info("=" * 60)
    logger.info("Embedding Preparation Completed")
    logger.info("=" * 60)

    return embedding_model, chunks


if __name__ == "__main__":

    embedding_model, chunks = prepare_embeddings()

    print()

    print("=" * 60)
    print("Embedding Test")
    print("=" * 60)

    vector = embedding_model.embed_query(
        chunks[0].page_content
    )

    print(f"Embedding Dimension : {len(vector)}")

    print()

    print(vector[:10])