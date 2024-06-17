"""Download pdfs."""
import requests
import os
import re
from urllib.parse import urlparse

from utils.lock import acquire_lock
from utils.logging import log
from constants import PDF_DIR, CONNECTION_STRING, CONTAINER_NAME
from azure.storage.blob import BlobServiceClient, BlobClient


def download(url: str) -> str:
    """Download a pdf file from a url and return the path to the file."""

    # path = os.path.join(PDF_DIR, normalize_filename(url) + ".pdf")
    # lock_path = path + ".lock"

    try:
        log("Downloading pdf from " + url)
        response = requests.get(url)

        parsed_url = urlparse(url)
        file_name = normalize_filename(os.path.basename(parsed_url.path))
    
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_name)
        
        # Upload the file content
        blob_client.upload_blob(response.content, overwrite=True)
        
        return file_name
    
    except Exception as e:
        log(f"Error uploading file: {e}")
        raise(f"Error uploading file: {e}")
    
    
    

    # with acquire_lock(lock_path):
    #     if os.path.exists(path):
    #         log("Pdf already exists in " + os.path.abspath(path))
    #         return path

    #     log("Downloading pdf from " + url)
    #     response = requests.get(url)

    #     with open(path, "wb") as f:
    #         f.write(response.content)

    #     return path


def normalize_filename(filename):
    """Replace any invalid characters with an underscore."""
    return re.sub(r"[^\w\-_. ]", "_", filename)
