"""
rag_pipeline.py

Complete Retrieval-Augmented Generation Pipeline.

Project : AgriAssist
"""

from retrieve import Retriever
from prompt import build_prompt
from llm import GeminiLLM
from logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:

    def __init__(self):

        logger.info("=" * 70)
        logger.info("Initializing AgriAssist")
        logger.info("=" * 70)

        self.retriever = Retriever()

        self.llm = GeminiLLM()

        logger.info("AgriAssist Ready")

    def ask(self, question: str):

        logger.info(f"Question : {question}")

        # -----------------------------
        # Retrieve documents
        # -----------------------------

        documents = self.retriever.search(question)

        # -----------------------------
        # Context
        # -----------------------------

        context = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        # -----------------------------
        # Prompt
        # -----------------------------

        prompt = build_prompt(
            context=context,
            question=question
        )

        # -----------------------------
        # LLM
        # -----------------------------

        answer = self.llm.generate(prompt)

        # -----------------------------
        # Sources
        # -----------------------------

        sources = []

        seen = set()

        for doc in documents:

            source = (
                doc.metadata.get("filename"),
                doc.metadata.get("page")
            )

            if source in seen:
                continue

            seen.add(source)

            sources.append({

                "filename": source[0],

                "page": source[1],

                "content": doc.page_content[:350]
            })

        return {

            "question": question,

            "answer": answer,

            "sources": sources,

            "retrieved_chunks": len(documents)

        }


if __name__ == "__main__":

    rag = RAGPipeline()

    print("=" * 70)
    print("🌱 AgriAssist")
    print("=" * 70)

    while True:

        question = input("\nAsk : ")

        if question.lower() == "exit":
            break

        result = rag.ask(question)

        print("\n")

        print("=" * 70)

        print(result["answer"])

        print("=" * 70)

        print("\nSources\n")

        for src in result["sources"]:

            print(

                f"{src['filename']}  (Page {src['page']})"

            )