"""
Configuration file for AgriAssist RAG Assistant.

This file stores all configurable parameters used across the project.
Changing a value here automatically updates the entire project.
"""

from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

PDF_DIR = DATA_DIR / "pdfs"

PROCESSED_DIR = DATA_DIR / "processed"

VECTOR_DB_DIR = PROJECT_ROOT / "vectordb"




# ==========================================================
# CHROMA DATABASE
# ==========================================================

COLLECTION_NAME = "agriassist"

REBUILD_INDEX = False

BATCH_SIZE = 500

# Logs directory
LOG_DIR = PROJECT_ROOT / "logs"

# ==========================================================
# PDF PROCESSING
# ==========================================================

SUPPORTED_EXTENSIONS = [".pdf"]

# ==========================================================
# CHUNKING CONFIGURATION
# ==========================================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ==========================================================
# EMBEDDING MODEL
# ==========================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DEVICE = "cpu"      # change to "cuda" if you have NVIDIA GPU

# ==========================================================
# RETRIEVAL
# ==========================================================

TOP_K = 5

SEARCH_TYPE = "similarity"

SEARCH_KWARGS = {
    "k": TOP_K
}

# ==========================================================
# LLM
# ==========================================================

LLM_MODEL = "gemini-2.5-flash"

# ==========================================================
# STREAMLIT
# ==========================================================

APP_TITLE = "AgriAssist"

WELCOME_MESSAGE = """
Hello 👋

I am AgriAssist.

Ask me anything related to

• Crops
• Fertilizers
• Pesticides
• Plant Diseases
• Irrigation
• Government Schemes

"""