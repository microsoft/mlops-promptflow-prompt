"""Invoke chat_with_pdf flow from Azure Function."""
import os
import azure.functions as func
from logging import WARNING, getLogger
from promptflow.client import load_flow, PFClient
from opentelemetry import trace
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

tracer = trace.get_tracer(__name__)
logger = getLogger(__name__)
logger.setLevel(WARNING)

OpenAIInstrumentor().instrument()


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="chatwithpdfinvoke")
def chat_with_pdf(req: func.HttpRequest) -> func.HttpResponse:
    """Invoke chat_with_pdf flow from Azure Function on HTTP trigger."""
    carrier = {'traceparent': req.headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("chatwithpdfinvoke", context=ctx):
        logger.info('Python HTTP trigger function processed a request.')

        try:
            req_body = req.get_json()
            if not isinstance(req_body, dict):
                return func.HttpResponse(
                    "String has been passed but json is expected",
                    status_code=400
                )
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
