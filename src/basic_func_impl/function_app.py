"""Invoking basic function flow from Azure Function."""
from logging import INFO, getLogger
import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor
from class_basic_invoke import bp as bp_class_based_invoke
from function_basic_invoke import bp as bp_function_based_invoke
from yaml_basic_invoke import bp as bp_yaml_based_invoke
from opentelemetry.instrumentation.openai import OpenAIInstrumentor


configure_azure_monitor(logger_name="functions")

logger = getLogger("functions")
logger.setLevel(INFO)


OpenAIInstrumentor().instrument()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(bp_class_based_invoke)
app.register_functions(bp_function_based_invoke)
app.register_functions(bp_yaml_based_invoke)