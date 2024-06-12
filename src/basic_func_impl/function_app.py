"""Invoking basic function flow from Azure Function."""
from logging import WARNING, getLogger
import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor
from class_basic_invoke import bp as bp_class_based_invoke
from function_basic_invoke import bp as bp_function_based_invoke
from yaml_basic_invoke import bp as bp_yaml_based_invoke
from opentelemetry.instrumentation.openai import OpenAIInstrumentor


configure_azure_monitor()

root_logger = getLogger()
root_logger.setLevel(WARNING)


OpenAIInstrumentor().instrument()

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(bp_class_based_invoke)
app.register_functions(bp_function_based_invoke)
app.register_functions(bp_yaml_based_invoke)
