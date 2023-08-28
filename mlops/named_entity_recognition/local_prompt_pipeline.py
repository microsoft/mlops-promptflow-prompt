import os
from dotenv import load_dotenv
from promptflow import PFClient
from promptflow.entities import Run

def main():
    load_dotenv()

    # Get a pf client to manage runs
    pf = PFClient()

    results = pf.run( 
        flow="./flows/named_entity_recognition/flows/standard",
        # run flow against local data or existing run, only one of data & run can be specified. 
        data="./flows/named_entity_recognition/data/data.jsonl",
        connections=
            {"NER_LLM": 
                {"connection": os.environ.get("AOAI_CONNECTION_NAME"),
                 "inputs.deployment_name": os.environ.get("AOAI_DEPLOYMENT_NAME")
                }
            }
    )

    print(results)
    pf.runs.visualize(results)

if __name__ == '__main__':
    main()