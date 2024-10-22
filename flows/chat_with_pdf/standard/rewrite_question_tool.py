"""Promptflow tool for re-writing question."""
from promptflow import tool
from chat_with_pdf.rewrite_question import rewrite_question


@tool
def rewrite_question_tool(question: str, history: list, env_ready_signal: str):
    """Re-write question base on chat history."""
    return rewrite_question(question, history)
