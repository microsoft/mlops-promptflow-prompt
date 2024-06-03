"""Invoking basic yaml flow from Azure Function."""

import logging
import os
import azure.functions as func
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from promptflow.client import load_flow, PFClient
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

bp = func.Blueprint()


@bp.route(route="functionbasedinvoke")
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
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

            flow_standard_path = os.path.join(os.path.dirname(__file__), "flow_code")

            flow = load_flow(flow_standard_path)
            flow.context = FlowContext(
                overrides={"nodes.NER_LLM.inputs.deployment_name": os.environ.get("AZURE_OPENAI_DEPLOYMENT")},
                connections={"NER_LLM": {"connection": connection}})
            result = flow(entity_type=entity_type, text=text)

            return func.HttpResponse(f"{result}", status_code=200)
        else:
            return func.HttpResponse("entity_type and text parameters have not been provided.", status_code=200)
