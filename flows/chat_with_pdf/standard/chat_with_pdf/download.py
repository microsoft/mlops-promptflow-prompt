"""Download pdfs."""
import requests
import os
import re
from urllib.parse import urlparse
from utils.logging import log
from constants import CONNECTION_STRING, PDFS_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient
from utils.create_container import create_container_if_not_exists
from constants import  PDFS_CONTAINER_NAME


def download(url: str) -> str:
    """Download a pdf file from a url and return the path to the file."""
    try:
        # Ensure the container exists
        create_container_if_not_exists(PDFS_CONTAINER_NAME)
        
        log("Downloading pdf from " + url)
        response = requests.get(url)

        parsed_url = urlparse(url)
        file_name = normalize_filename(os.path.basename(parsed_url.path))

        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=PDFS_CONTAINER_NAME, blob=file_name)
        
        # Upload the file content
        blob_client.upload_blob(response.content, overwrite=True)
        
        return file_name
    
    except Exception as e:
        log(f"Error uploading file: {e}")
        raise(f"Error uploading file: {e}")
    
def normalize_filename(filename):
    """Replace any invalid characters with an underscore."""
    return re.sub(r"[^\w\-_. ]", "_", filename)
