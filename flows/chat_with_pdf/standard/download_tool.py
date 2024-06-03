"""Promptflow tool for downloading by url."""
from promptflow import tool
from chat_with_pdf.download import download


@tool
def download_tool(url: str, env_ready_signal: str) -> str:
    """Download resource by provided url."""
    return download(url)
