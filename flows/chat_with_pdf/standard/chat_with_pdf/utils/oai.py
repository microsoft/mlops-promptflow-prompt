"""Helper classes to work with OpeAI API."""
from typing import List
import openai
from openai.version import VERSION as OPENAI_VERSION
import os
import tiktoken
from jinja2 import Template

from .retry import (
    retry_and_handle_exceptions,
    retry_and_handle_exceptions_for_generator,
)
from .logging import log


def extract_delay_from_rate_limit_error_msg(text):
    """Extract delay time from rate limit error message."""
    import re

    pattern = r"retry after (\d+)"
    match = re.search(pattern, text)
    if match:
        retry_time_from_message = match.group(1)
        return float(retry_time_from_message)
    else:
        return 5  # default retry time


class OAI:
    """OpenAI API client class."""

    def __init__(self):
        """Initialize the OAI class with API credentials and configuration."""
        self.check_openai_version()
        init_params = self.get_initial_params()
        api_type = os.environ.get("OPENAI_API_TYPE")
        self.initialize_client(api_type, init_params)
        self.sanity_checks(api_type, init_params)

    def check_openai_version(self):
        """Check the OpenAI package version."""
        if OPENAI_VERSION.startswith("0."):
            raise Exception(
                "Please upgrade your OpenAI package to version >= 1.0.0 or "
                "using the command: pip install --upgrade openai."
            )

    def get_initial_params(self):
        """Retrieve initial parameters from environment variables."""
        init_params = {}
        if os.getenv("OPENAI_API_VERSION") is not None:
            init_params["api_version"] = os.environ.get("OPENAI_API_VERSION")
        if os.getenv("OPENAI_ORG_ID") is not None:
            init_params["organization"] = os.environ.get("OPENAI_ORG_ID")
        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")

        init_params["api_key"] = os.environ.get("OPENAI_API_KEY")
        return init_params

    def sanity_checks(self, api_type, init_params):
        """Perform sanity checks on the initial parameters."""
        if api_type == "azure":
            if init_params.get("azure_endpoint") is None:
                raise ValueError(
                    "OPENAI_API_BASE is not set in environment variables, this is required when api_type==azure"
                )
            if init_params.get("api_version") is None:
                raise ValueError(
                    "OPENAI_API_VERSION is not set in environment variables, this is required when api_type==azure"
                )
            if init_params["api_key"].startswith("sk-"):
                raise ValueError(
                    "OPENAI_API_KEY should not start with sk- when api_type==azure, "
                    "are you using openai key by mistake?"
                )

    def initialize_client(self, api_type, init_params):
        """Initialize the OpenAI client."""
        if api_type == "azure":
            from openai import AzureOpenAI as Client
            init_params["azure_endpoint"] = os.environ.get("OPENAI_API_BASE")
        else:
            from openai import OpenAI as Client
            if os.getenv("OPENAI_API_BASE") is not None:
                init_params["base_url"] = os.environ.get("OPENAI_API_BASE")

        self.client = Client(**init_params)


class OAIChat(OAI):
    """OpenAI Chat API client class."""

    @retry_and_handle_exceptions(
        exception_to_check=(
            openai.RateLimitError,
            openai.APIStatusError,
            openai.APIConnectionError,
            KeyError,
        ),
        max_retries=5,
        extract_delay_from_error_message=extract_delay_from_rate_limit_error_msg,
    )
    def generate(self, messages: list, **kwargs) -> List[float]:
        """Generate a response from the chat API."""
        # chat api may return message with no content.
        message = self.client.chat.completions.create(
            model=os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME"),
            messages=messages,
            **kwargs,
        ).choices[0].message
        return getattr(message, "content", "")

    @retry_and_handle_exceptions_for_generator(
        exception_to_check=(
            openai.RateLimitError,
            openai.APIStatusError,
            openai.APIConnectionError,
            KeyError,
        ),
        max_retries=5,
        extract_delay_from_error_message=extract_delay_from_rate_limit_error_msg,
    )
    def stream(self, messages: list, **kwargs):
        """Stream a response from the chat API."""
        response = self.client.chat.completions.create(
            model=os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME"),
            messages=messages,
            stream=False,
            **kwargs,
        )

        return response.choices[0].message.content


class OAIEmbedding(OAI):
    """OpenAI Embedding API client class."""

    @retry_and_handle_exceptions(
        exception_to_check=openai.RateLimitError,
        max_retries=5,
        extract_delay_from_error_message=extract_delay_from_rate_limit_error_msg,
    )
    def generate(self, text: str) -> List[float]:
        """Generate an embedding for the given text."""
        return self.client.embeddings.create(
            input=text, model=os.environ.get("EMBEDDING_MODEL_DEPLOYMENT_NAME")
        ).data[0].embedding


def count_token(text: str) -> int:
    """Count the number of tokens in the given text."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def render_with_token_limit(template: Template, token_limit: int, **kwargs) -> str:
    """Render a Jinja2 template with a token limit."""
    text = template.render(**kwargs)
    token_count = count_token(text)
    if token_count > token_limit:
        message = f"token count {token_count} exceeds limit {token_limit}"
        log(message)
        raise ValueError(message)
    return text


if __name__ == "__main__":
    print(count_token("hello world, this is impressive"))
