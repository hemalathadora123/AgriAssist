"""
chunk.py

Splits loaded PDF documents into chunks for embedding.

Author: Hemalatha Dora
Project: AgriAssist
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import CHUNK_SIZE, CHUNK_OVERLAP
from ingest import load_documents
from logger import get_logger

logger = get_logger(__name__)


class DocumentChunker:
    """
    Splits LangChain Documents into smaller chunks.
    """

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def split_documents(
        self,
        documents: List[Document]
    ) -> List[Document]:
        """
        Split documents while preserving metadata.
        """

        logger.info("=" * 60)
        logger.info("Chunking Started")
        logger.info("=" * 60)

        chunks = self.text_splitter.split_documents(documents)

        logger.info(f"Total Chunks Created : {len(chunks)}")

        return chunks


def add_chunk_metadata(
    chunks: List[Document]
) -> List[Document]:
    """
    Add unique chunk IDs.
    """

    for idx, chunk in enumerate(chunks):

        chunk.metadata["chunk_id"] = idx

    return chunks


def print_statistics(
    documents: List[Document],
    chunks: List[Document]
):

    logger.info("=" * 60)
    logger.info("Chunk Statistics")
    logger.info("=" * 60)

    logger.info(f"Documents Loaded : {len(documents)}")
    logger.info(f"Chunks Created   : {len(chunks)}")

    avg = len(chunks) / len(documents)

    logger.info(f"Average Chunks / Page : {avg:.2f}")


def create_chunks() -> List[Document]:

    documents = load_documents()

    if not documents:

        logger.warning("No documents found.")

        return []

    chunker = DocumentChunker()

    chunks = chunker.split_documents(documents)

    chunks = add_chunk_metadata(chunks)

    print_statistics(documents, chunks)

    logger.info("=" * 60)
    logger.info("Chunking Completed Successfully")
    logger.info("=" * 60)

    return chunks


if __name__ == "__main__":

    chunks = create_chunks()

    print("\n")

    print("=" * 60)
    print("Sample Chunk")
    print("=" * 60)

    print(chunks[0].page_content[:800])

    print("\n")

    print("=" * 60)
    print("Metadata")
    print("=" * 60)

    print(chunks[0].metadata)