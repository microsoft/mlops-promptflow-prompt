"""Constants."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ACCOUNT_URL = os.getenv("ACCOUNT_URL")
PDFS_CONTAINER_NAME = "pdf-container"
INDEX_CONTAINER_NAME = "faiss-index"

