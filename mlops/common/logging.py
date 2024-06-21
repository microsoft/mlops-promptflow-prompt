import logging

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from promptflow.tracing._integrations._openai_injector import inject_openai_api
from promptflow.tracing import start_trace as start_pf_tracing
 
DEFAULT_LOG_LEVEL = 25

def log_output(*args):
    logging.log(DEFAULT_LOG_LEVEL, *args)

def init_logging(sampling_rate=1.0, log_level=DEFAULT_LOG_LEVEL):
    # Enable logging to app insights if a connection string is provided
    if 'APPLICATIONINSIGHTS_CONNECTION_STRING' in os.environ:
        connection_string=os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']
        if connection_string != "":
            inject_openai_api()
            trace.set_tracer_provider(TracerProvider(sampler=ParentBasedTraceIdRatio(sampling_rate)))
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=connection_string)))

    # Enable logging locally if the below variable is set
    if 'PROMPTFLOW_TRACING_SERVER' in os.environ and os.environ['PROMPTFLOW_TRACING_SERVER'] != 'false':
        start_pf_tracing()

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    log_output("Logging initialized.")