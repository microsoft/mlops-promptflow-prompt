"""Build index from pdfs."""
import PyPDF2
import faiss
import os

from pathlib import Path

from utils.oai import OAIEmbedding
from utils.index import FAISSIndex
from utils.logging import log
from utils.create_container import create_container_if_not_exists
from constants import CONNECTION_STRING, PDFS_CONTAINER_NAME, INDEX_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient
from io import BytesIO


def create_faiss_index(pdf_path: str) -> str:
    """Create faiss index from pdfs."""
    # Ensure the containerы exists
    create_container_if_not_exists(INDEX_CONTAINER_NAME)

    chunk_size = int(os.environ.get("CHUNK_SIZE"))
    chunk_overlap = int(os.environ.get("CHUNK_OVERLAP"))
    log(f"Chunk size: {chunk_size}, chunk overlap: {chunk_overlap}")

    file_name = Path(pdf_path).name + f".index_{chunk_size}_{chunk_overlap}"

    try:
        index = FAISSIndex(index=faiss.IndexFlatL2(1536), embedding=OAIEmbedding(), index_persistent_path=file_name)

        if index.index_blob_client.exists():
            log("Index already exists in Blob Storage, bypassing index creation")
            return file_name

        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=PDFS_CONTAINER_NAME, blob=pdf_path)

        # Download the file content
        blob_data = blob_client.download_blob().readall()

        # Read the PDF content
        pdf_reader = PyPDF2.PdfReader(BytesIO(blob_data))

        log("Building index")

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Chunk the words into segments of X words with Y-word overlap, X=CHUNK_SIZE, Y=OVERLAP_SIZE
        segments = split_text(text, chunk_size, chunk_overlap)

        log(f"Number of segments: {len(segments)}")

        index.insert_batch(segments)
        index.save()

        log("Index built: " + file_name)

        return file_name
    except Exception as e:
        log(f"Error reading file: {e}")
        raise (f"Error reading file: {e}")


# Split the text into chunks with CHUNK_SIZE and CHUNK_OVERLAP as character count
def split_text(text, chunk_size, chunk_overlap):
    """Split text in chunks."""
    # Calculate the number of chunks
    num_chunks = (len(text) - chunk_overlap) // (chunk_size - chunk_overlap)

    # Split the text into chunks
    chunks = []
    for i in range(num_chunks):
        start = i * (chunk_size - chunk_overlap)
        end = start + chunk_size
        chunks.append(text[start:end])

    # Add the last chunk
    chunks.append(text[num_chunks * (chunk_size - chunk_overlap):])

    return chunks
