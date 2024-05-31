"""Invoking basic class flow from Azure Function."""
import logging
import azure.functions as func
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from .flow_code.extract_entities import EntityExtraction

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("functions")

bp = func.Blueprint()


@bp.route(route="classbasedinvoke")
def class_based_invoke(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Invoke basic class flow from Azure Function."""
    carrier = {'traceparent': req.headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("function_based_invoke", context=ctx):
        logger.info('Python HTTP trigger function processed a request.')

        entity_type = req.params.get('entity_type')
        text = req.params.get('text')

        if entity_type and text:

            obj = EntityExtraction()
            result = obj(entity_type=entity_type, text=text)

            return func.HttpResponse(f"{result}", status_code=200)
        else:
            return func.HttpResponse("entity_type and text parameters have not been provided.", status_code=200)
