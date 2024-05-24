"""Promptflow Tool to build index."""
from promptflow import tool
from chat_with_pdf.build_index import create_faiss_index


@tool
def build_index_tool(pdf_path: str) -> str:
    """Build faiss index."""
    return create_faiss_index(pdf_path)
