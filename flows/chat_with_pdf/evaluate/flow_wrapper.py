"""Implement a wrapper for yaml based flow since it's not supported by evaluate explicitly."""
from promptflow.client import load_flow
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from promptflow.client import PFClient


class ChatWithPdfFlowWrapper:
    """Implement the flow."""

    def __init__(self, flow_config: dict, aoai_config: dict):
        """Initialize environment and load prompty into the memory."""
        connection = AzureOpenAIConnection(
            name=flow_config["connection_name"],
            api_key=aoai_config["aoai_api_key"],
            api_base=aoai_config["aoai_api_base"],
            api_type="azure",
            api_version=aoai_config["aoai_api_version"],
        )

        pf = PFClient()
        pf.connections.create_or_update(connection)

        self.flow = load_flow(flow_config["standard_flow_path"])
        self.flow.context = FlowContext(
            connections={"setup_env": {"connection": connection}},
            overrides={
                "inputs.config.default": {
                    "EMBEDDING_MODEL_DEPLOYMENT_NAME": flow_config[
                        "EMBEDDING_MODEL_DEPLOYMENT_NAME"
                    ],
                    "CHAT_MODEL_DEPLOYMENT_NAME": flow_config[
                        "CHAT_MODEL_DEPLOYMENT_NAME"
                    ],
                    "PROMPT_TOKEN_LIMIT": flow_config["PROMPT_TOKEN_LIMIT"],
                    "MAX_COMPLETION_TOKENS": flow_config["MAX_COMPLETION_TOKENS"],
                    "VERBOSE": flow_config["VERBOSE"],
                    "CHUNK_SIZE": flow_config["CHUNK_SIZE"],
                    "CHUNK_OVERLAP": flow_config["CHUNK_OVERLAP"],
                }
            },
        )

    def __call__(self, *, chat_history: str, pdf_url: str, question: str, **kwargs):
        """Invoke the flow for a single request."""
        return self.flow(chat_history=chat_history, pdf_url=pdf_url, question=question)
