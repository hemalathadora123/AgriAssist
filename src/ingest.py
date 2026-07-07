"""
Loads all PDFs from the data folder.

Output:
List of LangChain Document objects.
"""

import os
from typing import List
from utils import get_pdf_files
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from config import PDF_DIR, SUPPORTED_EXTENSIONS


def load_documents() -> List[Document]:
    """
    Load all PDF documents.

    Returns
    -------
    List[Document]
        List containing every page from every PDF.
    """

    documents = []

    pdf_files = get_pdf_files()

    from logger import get_logger

    logger = get_logger(__name__)

    logger.info("=" * 60)
    logger.info("Loading PDF Documents")
    logger.info(f"Found {len(pdf_files)} PDF files.")

    for index, file_path in enumerate(pdf_files, start=1):

        logger.info(f"[{index}/{len(pdf_files)}] Loading: {file_path.name}")

        try:

            loader = PyPDFLoader(str(file_path))

            pages = loader.load()

            logger.info(f"Pages Loaded: {len(pages)}")

            for page in pages:

                page.metadata["filename"] = file_path.name
                page.metadata["filepath"] = str(file_path)
                page.metadata["category"] = file_path.parent.name

            documents.extend(pages)

        except Exception as e:

            logger.error(f"Error loading {file_path.name}: {e}")

        pages = loader.load()

        print(f"Pages Loaded : {len(pages)}")
        for page in pages:

            page.metadata["filename"] = file_path.name
            page.metadata["filepath"] = str(file_path)
            page.metadata["category"] = file_path.parent.name
        documents.extend(pages)

    print("\n" + "=" * 60)
    print(f"Total Pages Loaded : {len(documents)}")
    print("=" * 60)

    return documents


if __name__ == "__main__":

    docs = load_documents()