"""The FastAPI application."""

from fastapi import FastAPI
from promptflow.client import load_flow, PFClient
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from .function_basic_flow.extract_entities import EntityExtraction
import os

app = FastAPI()


@app.get("/class_basic_flow")
def class_basic_flow(entity_type: str = None, text: str = None):
    """Return a message from the function_basic_flow endpoint."""
    if entity_type and text:
        connection = AzureOpenAIConnection(
            name="aoai",
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_type="azure",
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )

        pf = PFClient()
        pf.connections.create_or_update(connection)

        flow_standard_path = os.path.join(os.path.dirname(__file__), "class_basic_flow")

        flow = load_flow(flow_standard_path)
        flow.context = FlowContext(
            overrides={"nodes.NER_LLM.inputs.deployment_name": os.environ.get("AZURE_OPENAI_DEPLOYMENT")},
            connections={"NER_LLM": {"connection": connection}})
        result = flow(entity_type=entity_type, text=text)

        return {"result": result}
    else:
        return {"result": "class_basic_flow entity_type and text parameters have not been provided."}


@app.get("/function_basic_flow")
def function_basic_flow(entity_type: str = None, text: str = None):
    """Return a message from the class_basic_flow endpoint."""
    if entity_type and text:
        obj = EntityExtraction()
        result = obj(entity_type=entity_type, text=text)
        return {"result": result}
    else:
        return {"result": "function_basic_flow entity_type and text parameters have not been provided."}


@app.get("/yaml_basic_flow")
def yaml_basic_flow(entity_type: str = None, text: str = None):
    """Return a message from the yaml_basic_flow endpoint."""
    if entity_type and text:
        connection = AzureOpenAIConnection(
            name="aoai",
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_type="azure",
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )

        pf = PFClient()
        pf.connections.create_or_update(connection)

        flow_standard_path = os.path.join(os.path.dirname(__file__), "yaml_basic_flow")

        flow = load_flow(flow_standard_path)
        flow.context = FlowContext(
            overrides={"nodes.NER_LLM.inputs.deployment_name": os.environ.get("AZURE_OPENAI_DEPLOYMENT")},
            connections={"NER_LLM": {"connection": connection}})
        result = flow(entity_type=entity_type, text=text)

        return {"result": result}
    else:
        return {"result": "yaml_basic_flow entity_type and text parameters have not been provided."}