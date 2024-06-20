"""Invoke chat_with_pdf flow from Azure Function."""
import os
import azure.functions as func
import azure.durable_functions as df
from logging import WARNING, getLogger
from promptflow.client import load_flow, PFClient
from promptflow.entities import FlowContext, AzureOpenAIConnection
from opentelemetry import trace
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

configure_azure_monitor()

tracer = trace.get_tracer(__name__)
logger = getLogger(__name__)
logger.setLevel(WARNING)

OpenAIInstrumentor().instrument()

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.orchestration_trigger(context_name="context")
def orchestrator_function(context):
    req_body = context.get_input()
    result = yield context.call_activity("ChatWithPdf_ProcessRequest", req_body)
    return result

@app.function_name(name="ChatWithPdf_ProcessRequest")
@app.activity_trigger(input_name="reqbody")
def process_request(reqbody):
    config = reqbody.get("config")
    if config is None:
        config = {
            "EMBEDDING_MODEL_DEPLOYMENT_NAME": os.environ.get("EMBEDDING_MODEL_DEPLOYMENT_NAME"),
            "CHAT_MODEL_DEPLOYMENT_NAME": os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME"),
            "PROMPT_TOKEN_LIMIT": os.environ.get("PROMPT_TOKEN_LIMIT"),
            "MAX_COMPLETION_TOKENS": os.environ.get("MAX_COMPLETION_TOKENS"),
            "VERBOSE": os.environ.get("VERBOSE"),
            "CHUNK_SIZE": os.environ.get("CHUNK_SIZE"),
            "CHUNK_OVERLAP": os.environ.get("CHUNK_OVERLAP"),
        }
    
    chat_history = reqbody.get("chat_history") or []
    pdf_url = reqbody.get("pdf_url")
    question = reqbody.get("question")

    connection = AzureOpenAIConnection(
        name="aoai",
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_type="azure",
    )

    pf = PFClient()
    pf.connections.create_or_update(connection)

    flow_standard_path = os.path.join(os.path.dirname(__file__), "flow_code")
    flow = load_flow(flow_standard_path)
    flow.context = FlowContext(connections={"setup_env": {"connection": connection}})

    result = flow(chat_history=chat_history, pdf_url=pdf_url, question=question, config=config)
    return result

@app.function_name(name="chatwithpdfinvoke")
@app.route(route="chatwithpdfinvoke")
@app.durable_client_input(client_name="starter")
async def chat_with_pdf(req: func.HttpRequest, starter: df.DurableOrchestrationClient) -> func.HttpResponse:
    carrier = {"traceparent": req.headers["Traceparent"]}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("chatwithpdfinvoke", context=ctx):
        logger.info("Python HTTP trigger function processed a request.")
        try:
            req_body = req.get_json()
            if not isinstance(req_body, dict):
                return func.HttpResponse("Invalid JSON format", status_code=400)
        except ValueError:
            return func.HttpResponse("Invalid JSON", status_code=400)

        if not (req_body.get("question") and req_body.get("pdf_url")):
            return func.HttpResponse("Missing 'question' or 'pdf_url' parameter", status_code=400)

        try:
            instance_id = await starter.start_new("orchestrator_function", None, req_body)
            return starter.create_check_status_response(req, instance_id)
        except Exception as e:
            return func.HttpResponse(f"Error starting orchestration: {e}", status_code=500)
