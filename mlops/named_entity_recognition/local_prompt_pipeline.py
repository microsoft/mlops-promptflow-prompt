import os
from dotenv import load_dotenv
from promptflow import PFClient

def main():
    load_dotenv()

    # Get a pf client to manage runs
    pf = PFClient()

    results = pf.run( 
        flow="./flows/named_entity_recognition/standard",
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

    print(results)
    pf.runs.visualize(results)

if __name__ == '__main__':
    main()