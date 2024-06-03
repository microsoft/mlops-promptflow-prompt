"""Implement a wrapper for yaml based flow since it's not supported by evaluate explicitly."""
from promptflow.client import load_flow
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from promptflow.client import PFClient


class ChatWithPdfFlowWrapper:
    """Implement the flow."""

    def __init__(self, flow_standard_path: str, connection_name: str, aoai_deployment: str, aoai_config: dict):
        """Initialize environment and load prompty into the memory."""
        connection = AzureOpenAIConnection(
            name=connection_name,
            api_key=aoai_config["aoai_api_key"],
            api_base=aoai_config["aoai_api_base"],
            api_type="azure",
            api_version=aoai_config["aoai_api_version"],
        )

        pf = PFClient()
        pf.connections.create_or_update(connection)

        self.flow = load_flow(flow_standard_path)
        self.flow.context = FlowContext(
            connections={"setup_env": {"connection": connection}}
        )

    def __call__(self, *, chat_history: str, pdf_url: str, question: str, **kwargs):
        """Invoke the flow for a single request."""
        return self.flow(chat_history=chat_history, pdf_url=pdf_url, question=question)
