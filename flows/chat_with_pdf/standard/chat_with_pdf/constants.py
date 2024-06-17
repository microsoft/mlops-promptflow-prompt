"""Constants."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, ".pdfs")
INDEX_DIR = os.path.join(BASE_DIR, ".index/.pdfs/")

CONNECTION_STRING = os.getenv("AzureWebJobsStorage")
CONTAINER_NAME = "pdf-container"
