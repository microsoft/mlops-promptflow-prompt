import logging
import os
import azure.functions as func
from dotenv import load_dotenv
from .flow_code.extract_entities import extract_entity


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    load_dotenv()
    entity_type = req.params.get('entity_type')
    text = req.params.get('text')

    if entity_type and text:

        result = os.environ.get("AZURE_OPENAI_ENDPOINT") #extract_entity(entity_type=entity_type, text=text)

        return func.HttpResponse(f"{result}", status_code=200)
    else:
        return func.HttpResponse("entity_name and text parameters have not been provided.", status_code=200)
