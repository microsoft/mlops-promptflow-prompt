"""Promptflow tool for finding context in index."""
from promptflow import tool
from chat_with_pdf.find_context import find_context


@tool
def find_context_tool(question: str, index_path: str):
    """Find context in the provided index."""
    prompt, context = find_context(question, index_path)

    return {"prompt": prompt, "context": [c.text for c in context]}
