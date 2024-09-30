"""Create container in Azure Blob Storage."""
from constants import STORAGE_ACCOUNT_URL
from utils.logging import log
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


def create_container_if_not_exists(container_name: str):
    """Create container in Azure Blob Storage."""
    blob_service_client = BlobServiceClient(STORAGE_ACCOUNT_URL, DefaultAzureCredential())
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
        log(f"Container '{container_name}' created.")
    except Exception as e:
        if "ContainerAlreadyExists" in str(e):
            log(f"Container '{container_name}' already exists.")
        else:
            raise e
