"""Constants."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


STORAGE_ACCOUNT_URL = f"https://{os.getenv('STORAGE_ACCT_NAME')}.blob.core.windows.net/"
PDFS_CONTAINER_NAME = "pdf-container"
INDEX_CONTAINER_NAME = "faiss-index"
