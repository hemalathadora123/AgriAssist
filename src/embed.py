"""
embed.py

Loads embedding model and prepares documents for vector storage.

Uses FastEmbed (ONNX) instead of PyTorch so the app fits on
Render's free tier (~512MB RAM).
"""

from typing import List, Tuple

from langchain_core.documents import Document
from langchain_community.embeddings import FastEmbedEmbeddings

from chunking import create_chunks
from config import EMBEDDING_MODEL
from logger import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    """
    Wrapper around FastEmbed MiniLM embeddings.
    """

    def __init__(self):

        logger.info("=" * 60)
        logger.info("Loading Embedding Model (FastEmbed)")
        logger.info("=" * 60)

        self.model = FastEmbedEmbeddings(
            model_name=EMBEDDING_MODEL,
            batch_size=32,
            parallel=1,
        )

        logger.info(f"Embedding Model : {EMBEDDING_MODEL}")

    def get_model(self):

        return self.model


def prepare_embeddings() -> Tuple[
    FastEmbedEmbeddings,
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
