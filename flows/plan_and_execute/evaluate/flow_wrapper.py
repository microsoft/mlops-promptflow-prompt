"""Implement a wrapper for yaml based flow since it's not supported by evaluate explicitly."""
from promptflow.client import load_flow
from promptflow.entities import CustomConnection
from promptflow.client import PFClient


class PlanAndExecuteFlowWrapper:
    """Implement the flow."""

    def __init__(
        self,
        flow_standard_path: str,
        connection_name: str,
        connection_secrets: dict,
        connection_configs: dict,
    ):
        """Initialize environment and load prompty into the memory."""
        connection = CustomConnection(
            name=connection_name, secrets=connection_secrets, configs=connection_configs
        )

        pf = PFClient()
        pf.connections.create_or_update(connection)

        self.flow = load_flow(flow_standard_path)

    def __call__(self, *, question: str, **kwargs):
        """Invoke the flow for a single request."""
        return self.flow(question=question)
