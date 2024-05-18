"""Implement PromptFlow flow as a class."""
import os
import pathlib
from typing import List
from promptflow.core import Prompty


class EntityExtraction:
    """Implement the flow."""

    def __init__(self):
        """Initialize environment and load prompty into the memory."""
        override_model = {
            "configuration": {
                "azure_deployment": "${env:AZURE_OPENAI_DEPLOYMENT}",
                "api_key": "${env:AZURE_OPENAI_API_KEY}",
                "api_version": "${env:AZURE_OPENAI_API_VERSION}",
                "azure_endpoint": "${env:AZURE_OPENAI_ENDPOINT}"
            }
        }
        rootpath = pathlib.Path(__file__).parent.resolve()

        self.prompty = Prompty.load(
            source=os.path.join(rootpath, "entity_template.prompty"),
            model=override_model,
        )

    def __call__(self, *, entity_type: str, text: str, **kwargs):
        """Invoke the flow for a single request."""
        result = self.prompty(entity_type=entity_type, text=text)

        output = self.cleansing(result)

        return {"answer": output}

    def cleansing(self, entities_str: str) -> List[str]:
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
