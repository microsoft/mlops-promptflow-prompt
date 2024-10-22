"""This is a Prompt flow tool that we are using in standard flow."""
from typing import List
from promptflow.core import tool


@tool
def cleansing(entities_str: str) -> List[str]:
    """
    Return a list of cleaned entities. Split, remove leading and trailing spaces/tabs/dots.

    Parameters:
      entities_str (string): a string with comma separated entities

    Returns:
        list<str>: a list of cleaned entities
    """
    parts = entities_str.split(",")
    cleaned_parts = [part.strip(' \t."') for part in parts]
    entities = [part for part in cleaned_parts if len(part) > 0]
    return entities
