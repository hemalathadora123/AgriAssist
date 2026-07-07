"""
utils.py

Common utility functions used throughout the project.
"""

from pathlib import Path
from typing import List

from config import PDF_DIR, SUPPORTED_EXTENSIONS


def get_pdf_files() -> List[Path]:
    """
    Returns all PDF files from the PDF directory.

    Returns
    -------
    List[Path]
    """

    pdf_files = []

    for file in PDF_DIR.iterdir():

        if file.suffix.lower() in SUPPORTED_EXTENSIONS:
            pdf_files.append(file)

    pdf_files.sort()

    return pdf_files


def ensure_directories():
    """
    Creates required directories if they don't exist.
    """

    from config import (
        VECTOR_DB_DIR,
        LOG_DIR,
        PROCESSED_DIR,
    )

    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)