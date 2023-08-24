from promptflow import PFClient
from promptflow.entities import Run

def main():
    # Get a pf client to manage runs
    pf = PFClient()

    results = pf.run( 
        flow="./flows/basic_with_llm",
        # run flow against local data or existing run, only one of data & run can be specified. 
        data="./flows/basic_with_llm/data.jsonl"
    )

    print(results)
    pf.runs.visualize(results)

if __name__ == '__main__':
    main()
