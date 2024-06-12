"""Invoking basic class flow from Azure Function."""
import logging
import os
import azure.functions as func
from promptflow.core import AzureOpenAIModelConfiguration
from promptflow.entities import AzureOpenAIConnection
from opentelemetry import trace
from promptflow.client import PFClient
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from class_basic_invoke.extract_entities import EntityExtraction

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = func.Blueprint()


@bp.route(route="classbasicinvoke")
def class_basic_invoke(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Invoke basic class flow from Azure Function."""
    carrier = {'traceparent': req.headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("class_basic_invoke", context=ctx):
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
