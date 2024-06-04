"""Implement PromptFlow flow as a class."""
import os
import pathlib
from typing import List
from promptflow.core import Prompty, AzureOpenAIModelConfiguration
from promptflow.tracing import trace


class EntityExtraction:
    """Implement the flow."""

    def __init__(self, model_config: AzureOpenAIModelConfiguration):
        """Initialize environment and load prompty into the memory."""
        rootpath = pathlib.Path(__file__).parent.resolve()

        self.model_config = model_config

        self.prompty = Prompty.load(
            source=os.path.join(rootpath, "entity_template.prompty"),
            model={"configuration": self.model_config},
        )

    @trace
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
