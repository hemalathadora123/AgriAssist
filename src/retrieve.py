"""
retrieve.py

Loads an existing ChromaDB and retrieves
relevant chunks for a given query.
"""

from typing import List

from langchain_core.documents import Document

from logger import get_logger
from vector_store import VectorStoreManager
from config import SEARCH_KWARGS

logger = get_logger(__name__)


class Retriever:

    def __init__(self):

        logger.info("Loading Vector Database...")

        manager = VectorStoreManager()

        self.db = manager.load()

        self.retriever = self.db.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "fetch_k": 20,
                "lambda_mult": 0.7
            }
        )

        logger.info("Retriever Ready.")

    def search(
        self,
        question: str
    ) -> List[Document]:

        logger.info(f"Question : {question}")

        docs = self.retriever.invoke(question)

        logger.info(f"Retrieved {len(docs)} chunks.")

        return docs


if __name__ == "__main__":

    retriever = Retriever()

    question = input("\nAsk a Question : ")

    documents = retriever.search(question)

    print("\n")

    print("=" * 70)

    print("Retrieved Documents")

    print("=" * 70)

    for i, doc in enumerate(documents, start=1):

        print(f"\nResult {i}")

        print("-" * 50)

        print("Filename :", doc.metadata.get("filename"))

        print("Page :", doc.metadata.get("page"))

        print()

        print(doc.page_content[:500])

        print()