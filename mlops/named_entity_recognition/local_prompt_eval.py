import json
import os
from dotenv import load_dotenv
from promptflow import PFClient

def main():
    load_dotenv()
    
    # Get a pf client to manage runs
    pf = PFClient()

    base_run = pf.run( 
        flow="./flows/named_entity_recognition/standard",
        # run flow against local data or existing run, only one of data & run can be specified. 
        data="./flows/named_entity_recognition/data/data.jsonl",
        connections=
            {"NER_LLM": 
                {
                    "connection": os.environ.get("AOAI_CONNECTION_NAME"),
                    # this line is doing nothing due to a bug
                    "deployment_name": os.environ.get("AOAI_DEPLOYMENT_NAME")
                }
            }
    )

    # run the flow with exisiting run
    eval_run = pf.run(
        flow="./flows/named_entity_recognition/evaluation",
        data="./flows/named_entity_recognition/data/eval_data.jsonl",
        run=base_run,
        column_mapping={
                "ground_truth": "${data.results}",
                "entities": "${run.outputs.entities}",
            }  # map the url field from the data to the url input of the flow
    )

    # stream the run until it's finished
    pf.stream(eval_run)

    # get the inputs/outputs details of a finished run.
    details = pf.get_details(eval_run)
    details.head(10)

    # view the metrics of the eval run
    metrics = pf.get_metrics(eval_run)
    print(json.dumps(metrics, indent=4))

if __name__ == '__main__':
    main()