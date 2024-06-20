"""Constants."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION")
PDFS_CONTAINER_NAME = "pdf-container"
INDEX_CONTAINER_NAME = "faiss-index"
