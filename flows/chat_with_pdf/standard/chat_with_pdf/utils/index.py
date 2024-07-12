"""Faiss index class."""
import os
from typing import Iterable, List, Optional
from dataclasses import dataclass
import faiss
import pickle
import tempfile
import numpy as np
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.identity import DefaultAzureCredential
from utils.logging import log
from .oai import OAIEmbedding as Embedding
from constants import STORAGE_ACCOUNT_URL, INDEX_CONTAINER_NAME


@dataclass
class SearchResultEntity:
    """Data class for search results."""

    text: str = None
    vector: List[float] = None
    score: float = None
    original_entity: dict = None
    metadata: dict = None


INDEX_FILE_NAME = "index.faiss"
DATA_FILE_NAME = "index.pkl"


class FAISSIndex:
    """Faiss index class."""

    def __init__(self, index: faiss.Index, embedding: Embedding, index_persistent_path: str) -> None:
        """Initialize Faiss index class."""
        self.index = index
        self.docs = {}  # id -> doc, doc is (text, metadata)
        self.embedding = embedding
        self.index_persistent_path = index_persistent_path + INDEX_FILE_NAME
        self.docs_persistent_path = index_persistent_path + DATA_FILE_NAME
        self.blob_service_client = BlobServiceClient(STORAGE_ACCOUNT_URL, DefaultAzureCredential())
        self.index_blob_client = self._get_blob_client(self.index_persistent_path)
        self.docs_blob_client = self._get_blob_client(self.docs_persistent_path)

    def _get_blob_client(self, blob_path: str) -> BlobClient:
        return self.blob_service_client.get_blob_client(container=INDEX_CONTAINER_NAME, blob=blob_path)

    def insert_batch(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None) -> None:
        """Insert batch into index."""
        documents, vectors = [], []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            vector = self.embedding.generate(text)
            documents.append((text, metadata))
            vectors.append(vector)

        self.index.add(np.array(vectors, dtype=np.float32))
        self.docs.update({i: doc for i, doc in enumerate(documents, start=len(self.docs))})

    def query(self, text: str, top_k: int = 10) -> List[SearchResultEntity]:
        """Query index."""
        vector = self.embedding.generate(text)
        scores, indices = self.index.search(np.array([vector], dtype=np.float32), top_k)
        return [
            SearchResultEntity(text=self.docs[i][0], metadata=self.docs[i][1], score=scores[0][j])
            for j, i in enumerate(indices[0]) if i != -1
        ]

    def save(self) -> None:
        """Save index to Azure Blob Storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self._save_index_to_temp(temp_dir)
            self._upload_index_to_blob(temp_dir)
            log(f"Index uploaded to Blob Storage: {self.index_persistent_path}")

    def _save_index_to_temp(self, temp_dir: str) -> None:
        faiss.write_index(self.index, os.path.join(temp_dir, INDEX_FILE_NAME))
        with open(os.path.join(temp_dir, DATA_FILE_NAME), "wb") as f:
            pickle.dump(self.docs, f)

    def _upload_index_to_blob(self, temp_dir: str) -> None:
        self._upload_file_to_blob(os.path.join(temp_dir, INDEX_FILE_NAME), self.index_blob_client)
        self._upload_file_to_blob(os.path.join(temp_dir, DATA_FILE_NAME), self.docs_blob_client)

    def _upload_file_to_blob(self, local_path: str, blob_client: BlobClient) -> None:
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

    def load(self) -> faiss.Index:
        """Load faiss index from Azure Blob Storage."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                self._download_index_to_temp(temp_dir)
                self._load_index_from_temp(temp_dir)
            log("FAISS index loaded into memory")
        except Exception as e:
            log(f"Error loading FAISS index: {e}")
            raise e

    def _download_index_to_temp(self, temp_dir: str) -> None:
        self._download_blob_to_temp(self.index_blob_client, os.path.join(temp_dir, INDEX_FILE_NAME))
        self._download_blob_to_temp(self.docs_blob_client, os.path.join(temp_dir, DATA_FILE_NAME))

    def _download_blob_to_temp(self, blob_client: BlobClient, local_path: str) -> None:
        with open(local_path, "wb") as file:
            blob_client.download_blob().readinto(file)
        log(f"Downloaded blob to {local_path}")

    def _load_index_from_temp(self, temp_dir: str) -> None:
        self.index = faiss.read_index(os.path.join(temp_dir, INDEX_FILE_NAME))
        with open(os.path.join(temp_dir, DATA_FILE_NAME), "rb") as f:
            self.docs = pickle.load(f)
