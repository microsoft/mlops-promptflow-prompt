import logging
import azure.functions as func
from .flow_code.extract_entities import EntityExtraction


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    entity_type = req.params.get('entity_type')
    text = req.params.get('text')

    if entity_type and text:

        obj = EntityExtraction()
        result = obj(entity_type=entity_type, text=text)

        return func.HttpResponse(f"{result}", status_code=200)
    else:
        return func.HttpResponse("entity_type and text parameters have not been provided.", status_code=200)
