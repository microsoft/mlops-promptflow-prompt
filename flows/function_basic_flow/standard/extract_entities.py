"""function_basic_flow implementation."""
import pathlib
import os
from promptflow.tracing import trace
from promptflow.core import Prompty
from .cleansing import cleansing


# @trace
def extract_entity(entity_type: str, text: str):
    """Implement the flow as a function."""
    override_model = {
        "configuration": {
            "azure_deployment": "${env:AZURE_OPENAI_DEPLOYMENT}",
            "api_key": "${env:AZURE_OPENAI_API_KEY}",
            "api_version": "${env:AZURE_OPENAI_API_VERSION}",
            "azure_endpoint": "${env:AZURE_OPENAI_ENDPOINT}"
        }
    }
    rootpath = pathlib.Path(__file__).parent.resolve()

    prompty = Prompty.load(
        source=os.path.join(rootpath, "entity_template.prompty"),
        model=override_model,
    )

    result = prompty(entity_type=entity_type, text=text)

    output = cleansing(result)

    return {"answer": output}


if __name__ == "__main__":
    print(extract_entity(
        "people's full name",
        "The novel 'The Great Gatsby' was written by F. Scott Fitzgerald.")
    )
