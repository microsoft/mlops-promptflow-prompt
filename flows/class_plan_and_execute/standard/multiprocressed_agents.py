"""
Multi-processed agents for the class plan and execute flow.

Necessary for pickling the agents for multiprocessing when using promptflow eval.
"""
from autogen import AssistantAgent, UserProxyAgent
from autogen.oai.client import OpenAIWrapper
from autogen.code_utils import content_str
from typing import Dict


def _is_default_termination_msg(message: Dict) -> bool:
    return content_str(message.get("content")) == "TERMINATE"


class MultiProcessedAssistantAgent(AssistantAgent):
    """AssistantAgent that can be pickled for multiprocessing."""

    def __init__(self, *args, **kwargs):
        """Extract is_termination_msg if provided."""
        is_termination_msg = kwargs.pop("is_termination_msg", None)
        super().__init__(*args, **kwargs)
        self._is_termination_msg = (
            is_termination_msg
            if is_termination_msg is not None
            else _is_default_termination_msg
        )

    def __getstate__(self):
        """Create a state dictionary, excluding unpickleable objects."""
        state = self.__dict__.copy()
        if "client" in state:
            state[
                "client"
            ] = None  # Exclude the client (and its SSLContext) from being pickled
        return state

    def __setstate__(self, state):
        """Restore the state."""
        self.__dict__.update(state)
        # Reinitialize the client or the SSLContext
        if self.client is None:
            # Use actual initialization parameters for OpenAIWrapper
            self.client = OpenAIWrapper(**self.llm_config)


class MultiProcessedUserProxyAgent(UserProxyAgent):
    """UserProxyAgent that can be pickled for multiprocessing."""

    def __init__(self, *args, **kwargs):
        """Extract is_termination_msg if provided."""
        is_termination_msg = kwargs.pop("is_termination_msg", None)
        super().__init__(*args, **kwargs)
        self._is_termination_msg = (
            is_termination_msg
            if is_termination_msg is not None
            else _is_default_termination_msg
        )

    def __getstate__(self):
        """Create a state dictionary, excluding unpickleable objects."""
        state = self.__dict__.copy()
        if "client" in state:
            state[
                "client"
            ] = None  # Exclude the client (and its SSLContext) from being pickled
        return state

    def __setstate__(self, state):
        """Restore the state."""
        self.__dict__.update(state)
        # Reinitialize the client or the SSLContext
        if self.client is None:
            # Use actual initialization parameters for OpenAIWrapper
            self.client = OpenAIWrapper(**self.llm_config)
