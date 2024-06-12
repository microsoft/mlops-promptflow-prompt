"""Invoking basic function flow from Azure Function."""
import logging
import azure.functions as func
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from function_basic_invoke_flow_code.extract_entities import extract_entity

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = func.Blueprint()


@bp.route(route="functionbasicinvoke")
def function_basic_invoke(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Invoke basic function flow from Azure Function."""
    carrier = {'traceparent': req.headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    with tracer.start_as_current_span("function_basic_invoke", context=ctx):
        logger.info('Python HTTP trigger function processed a request.')

        entity_type = req.params.get('entity_type')
        text = req.params.get('text')

        if entity_type and text:

            result = extract_entity(entity_type=entity_type, text=text)

            return func.HttpResponse(f"{result}", status_code=200)
        else:
            return func.HttpResponse("entity_type and text parameters have not been provided.", status_code=200)
