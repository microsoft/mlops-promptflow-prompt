"""Invoke chat_with_pdf flow from Azure Function."""
import os
import azure.functions as func
import logging

from promptflow.client import load_flow, PFClient
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="chatwithpdfinvoke")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Invoke chat_with_pdf flow from Azure Function on HTTP trigger."""
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON",
            status_code=400
        )

    chat_history = req_body.get('chat_history')
    pdf_url = req_body.get('pdf_url')
    question = req_body.get('question')

    if question and pdf_url:
        if chat_history is None:
            chat_history = []

        connection = AzureOpenAIConnection(
            name="aoai",
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_type="azure",
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )

        pf = PFClient()
        pf.connections.create_or_update(connection)

        flow_standard_path = os.path.join(os.path.dirname(__file__), "flow_code")
        flow = load_flow(flow_standard_path)
        flow.context = FlowContext(
            connections={"setup_env": {"connection": connection}},
        )

        config = req_body.get('config')
        if config is None:
            config = {
                "EMBEDDING_MODEL_DEPLOYMENT_NAME": os.environ.get("EMBEDDING_MODEL_DEPLOYMENT_NAME"),
                "CHAT_MODEL_DEPLOYMENT_NAME": os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME"),
                "PROMPT_TOKEN_LIMIT": os.environ.get("PROMPT_TOKEN_LIMIT"),
                "MAX_COMPLETION_TOKENS": os.environ.get("MAX_COMPLETION_TOKENS"),
                "VERBOSE": os.environ.get("VERBOSE"),
                "CHUNK_SIZE": os.environ.get("CHUNK_SIZE"),
                "CHUNK_OVERLAP": os.environ.get("CHUNK_OVERLAP")
            }

        result = flow(chat_history=chat_history, pdf_url=pdf_url, question=question, config=config)

        return func.HttpResponse(f"{result}", status_code=200)
    else:
        return func.HttpResponse("question and pdf_url parameters have not been provided.", status_code=200)
