"""Invoking basic function flow from Azure Function."""
import logging
import os
import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor
from class_basic_invoke import bp as bp_class_based_invoke
from function_basic_invoke import bp as bp_function_based_invoke
from yaml_basic_invoke import bp as bp_yaml_based_invoke
from opentelemetry.instrumentation.openai import OpenAIInstrumentor


configure_azure_monitor()

logging.getLogger("azure").setLevel(os.environ.get("LOGLEVEL_AZURE", "WARN").upper())

OpenAIInstrumentor().instrument()

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(bp_class_based_invoke)
app.register_functions(bp_function_based_invoke)
app.register_functions(bp_yaml_based_invoke)
