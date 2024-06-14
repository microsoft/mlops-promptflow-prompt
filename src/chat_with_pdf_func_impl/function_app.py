"""Invoke chat_with_pdf flow from Azure Function."""
import os
import azure.functions as func
import azure.durable_functions as df
from logging import WARNING, getLogger
from promptflow.client import load_flow, PFClient
from opentelemetry import trace
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from azure.monitor.opentelemetry import configure_azure_monitor

# configure_azure_monitor()

# tracer = trace.get_tracer(__name__)
# logger = getLogger(__name__)
# logger.setLevel(WARNING)

# OpenAIInstrumentor().instrument()

import azure.functions as func
import azure.durable_functions as df

# myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# # An HTTP-Triggered Function with a Durable Functions Client binding
# @myApp.route(route="orchestrators/{functionName}")
# @myApp.durable_client_input(client_name="client")
# async def http_start(req: func.HttpRequest, client):
#     function_name = req.route_params.get('functionName')
#     instance_id = await client.start_new(function_name)
#     response = client.create_check_status_response(req, instance_id)
#     return response

# # Orchestrator
# @myApp.orchestration_trigger(context_name="context")
# def hello_orchestrator(context):
#     result1 = yield context.call_activity("hello", "Seattle")
#     result2 = yield context.call_activity("hello", "Tokyo")
#     result3 = yield context.call_activity("hello", "London")

#     return [result1, result2, result3]

# # Activity
# @myApp.activity_trigger(input_name="city")
# def hello(city: str):
#     return f"Hello {city}"

# app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)


# async def orchestrator_function(context: df.DurableOrchestrationContext):
#     req_body = context.get_input()
    
#     # Call activity functions in sequence
#     config = await context.call_activity("ChatWithPdf_GetConfig", req_body)
#     result = await context.call_activity("ChatWithPdf_ProcessRequest", (req_body, config))
    
#     return result

# main = df.Orchestrator.create(orchestrator_function)


# @app.function_name(name="ChatWithPdf_GetConfig")
# @app.route(route="getconfig")
# @app.durable_activity_trigger(input_name="req_body")
# def get_config(req_body):
#     config = req_body.get("config")
#     if config is None:
#         config = {
#             "EMBEDDING_MODEL_DEPLOYMENT_NAME": os.environ.get("EMBEDDING_MODEL_DEPLOYMENT_NAME"),
#             "CHAT_MODEL_DEPLOYMENT_NAME": os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME"),
#             "PROMPT_TOKEN_LIMIT": os.environ.get("PROMPT_TOKEN_LIMIT"),
#             "MAX_COMPLETION_TOKENS": os.environ.get("MAX_COMPLETION_TOKENS"),
#             "VERBOSE": os.environ.get("VERBOSE"),
#             "CHUNK_SIZE": os.environ.get("CHUNK_SIZE"),
#             "CHUNK_OVERLAP": os.environ.get("CHUNK_OVERLAP"),
#         }
#     return config


# @app.function_name(name="ChatWithPdf_ProcessRequest")
# @app.route(route="processrequest")
# @app.durable_activity_trigger(input_name="params")
# def process_request(params):
#     req_body, config = params
    
#     chat_history = req_body.get("chat_history")
#     pdf_url = req_body.get("pdf_url")
#     question = req_body.get("question")

#     if chat_history is None:
#         chat_history = []

#     connection = AzureOpenAIConnection(
#         name="aoai",
#         api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
#         api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
#         api_type="azure",
#         api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
#     )

#     pf = PFClient()
#     pf.connections.create_or_update(connection)

#     flow_standard_path = os.path.join(os.path.dirname(__file__), "flow_code")
#     flow = load_flow(flow_standard_path)
#     flow.context = FlowContext(
#         connections={"setup_env": {"connection": connection}},
#     )

#     result = flow(
#         chat_history=chat_history,
#         pdf_url=pdf_url,
#         question=question,
#         config=config,
#     )
#     return result


# @app.function_name(name="chatwithpdfinvoke")
# @app.route(route="chatwithpdfinvoke")
# @app.durable_client_input(client_name="starter")
# async def chat_with_pdf(req: func.HttpRequest, starter: df.DurableOrchestrationClient) -> func.HttpResponse:
#     """Invoke chat_with_pdf flow from Azure Durable Function on HTTP trigger."""
#     carrier = {"traceparent": req.headers.get("Traceparent")}
#     ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

#     with tracer.start_as_current_span("chatwithpdfinvoke", context=ctx):
#         logger.info("Python HTTP trigger function processed a request.")

#         try:
#             req_body = req.get_json()
#             if not isinstance(req_body, dict):
#                 return func.HttpResponse(
#                     "String has been passed but json is expected", status_code=400
#                 )
#         except ValueError:
#             return func.HttpResponse("Invalid JSON", status_code=400)

#         if req_body.get("question") and req_body.get("pdf_url"):
#             instance_id = await starter.start_new("orchestrator_function", req_body)
#             return starter.create_check_status_response(req, instance_id)
#         else:
#             return func.HttpResponse(
#                 "question and pdf_url parameters have not been provided.",
#                 status_code=400,
#             )

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="chatwithpdfinvoke")
def chat_with_pdf(req: func.HttpRequest) -> func.HttpResponse:
    """Invoke chat_with_pdf flow from Azure Function on HTTP trigger."""
    carrier = {"traceparent": req.headers["Traceparent"]}
    # ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    # with tracer.start_as_current_span("chatwithpdfinvoke", context=ctx):
    #     logger.info("Python HTTP trigger function processed a request.")
    if True:
        try:
            req_body = req.get_json()
            if not isinstance(req_body, dict):
                return func.HttpResponse(
                    "String has been passed but json is expected", status_code=400
                )
        except ValueError:
            return func.HttpResponse("Invalid JSON", status_code=400)

        chat_history = req_body.get("chat_history")
        pdf_url = req_body.get("pdf_url")
        question = req_body.get("question")

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

            config = req_body.get("config")
            if config is None:
                config = {
                    "EMBEDDING_MODEL_DEPLOYMENT_NAME": os.environ.get(
                        "EMBEDDING_MODEL_DEPLOYMENT_NAME"
                    ),
                    "CHAT_MODEL_DEPLOYMENT_NAME": os.environ.get(
                        "CHAT_MODEL_DEPLOYMENT_NAME"
                    ),
                    "PROMPT_TOKEN_LIMIT": os.environ.get("PROMPT_TOKEN_LIMIT"),
                    "MAX_COMPLETION_TOKENS": os.environ.get("MAX_COMPLETION_TOKENS"),
                    "VERBOSE": os.environ.get("VERBOSE"),
                    "CHUNK_SIZE": os.environ.get("CHUNK_SIZE"),
                    "CHUNK_OVERLAP": os.environ.get("CHUNK_OVERLAP"),
                }

            result = flow(
                chat_history=chat_history,
                pdf_url=pdf_url,
                question=question,
                config=config,
            )

            return func.HttpResponse(f"{result}", status_code=200)
        else:
            return func.HttpResponse(
                "question and pdf_url parameters have not been provided.",
                status_code=200,
            )
