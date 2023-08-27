from promptflow import PFClient
from promptflow.entities import Run

def main():
    # Get a pf client to manage runs
    pf = PFClient()

    results = pf.run( 
        flow="./flows/named_entity_recognition/flows/standard",
        # run flow against local data or existing run, only one of data & run can be specified. 
        data="./flows/named_entity_recognition/data/data.jsonl"
    )

    print(results)
    pf.runs.visualize(results)

if __name__ == '__main__':
    main()