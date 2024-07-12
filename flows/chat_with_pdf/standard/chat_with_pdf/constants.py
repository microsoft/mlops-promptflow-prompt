"""Constants."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STORAGE_ACCOUNT_URL = os.getenv("STORAGE_ACCOUNT_URL")
PDFS_CONTAINER_NAME = "pdf-container"
INDEX_CONTAINER_NAME = "faiss-index"
