"""Invoking basic function flow from Azure Function."""
import os
from logging import WARNING, getLogger
import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from promptflow.core import AzureOpenAIModelConfiguration
from promptflow.entities import AzureOpenAIConnection
from promptflow.client import load_flow, PFClient
from promptflow.entities import FlowContext

from class_basic_invoke.flow_code.extract_entities import EntityExtraction
from function_basic_invoke.flow_code.extract_entities import extract_entity


configure_azure_monitor()

logger = getLogger(__name__)
tracer = trace.get_tracer(__name__)
logger.setLevel(WARNING)


OpenAIInstrumentor().instrument()

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="functionbasicinvoke")
def function_basic_invoke(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Invoke basic function flow from Azure Function."""
    carrier = {'traceparent': req.headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("function_based_invoke", context=ctx):
        logger.info('Python HTTP trigger function processed a request.')

        entity_type = req.params.get('entity_type')
        text = req.params.get('text')

        if entity_type and text:

            result = extract_entity(entity_type=entity_type, text=text)

            return func.HttpResponse(f"{result}", status_code=200)
        else:
            return func.HttpResponse("entity_type and text parameters have not been provided.", status_code=200)


@app.route(route="classbasicinvoke")
def class_basic_invoke(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Invoke basic class flow from Azure Function."""
    carrier = {'traceparent': req.headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("function_based_invoke", context=ctx):
        logger.info('Python HTTP trigger function processed a request.')

        entity_type = req.params.get('entity_type')
        text = req.params.get('text')

        if entity_type and text:

            connection = AzureOpenAIConnection(
                name="aoai",  # it's just a local name, and it can be any
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                api_type="azure",
                api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            )

            pf = PFClient()
            pf.connections.create_or_update(connection)

            # create the model config to be used in below flow calls
            config = AzureOpenAIModelConfiguration(
                connection="aoai", azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT")
            )

            obj = EntityExtraction(model_config=config)
            result = obj(entity_type=entity_type, text=text)

            return func.HttpResponse(f"{result}", status_code=200)
        else:
            return func.HttpResponse("entity_type and text parameters have not been provided.", status_code=200)


@app.route(route="yamlbasicinvoke")
def yaml_basic_invoke(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Invoke basic yaml flow from Azure Function."""
    carrier = {'traceparent': req.headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("function_based_invoke", context=ctx):
        logger.info('Python HTTP trigger function processed a request.')

        entity_type = req.params.get('entity_type')
        text = req.params.get('text')

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

            flow_standard_path = os.path.join(os.path.dirname(__file__), "yaml_basic_invoke/flow_code")

            flow = load_flow(flow_standard_path)
            flow.context = FlowContext(
                overrides={"nodes.NER_LLM.inputs.deployment_name": os.environ.get("AZURE_OPENAI_DEPLOYMENT")},
                connections={"NER_LLM": {"connection": connection}})
            result = flow(entity_type=entity_type, text=text)

            return func.HttpResponse(f"{result}", status_code=200)
        else:
            return func.HttpResponse("entity_type and text parameters have not been provided.", status_code=200)
