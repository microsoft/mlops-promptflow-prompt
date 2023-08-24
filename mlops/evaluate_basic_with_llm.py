import json
from promptflow import PFClient
from promptflow.entities import Run

def main():
    # Get a pf client to manage runs
    pf = PFClient()

    base_run = pf.run( 
        flow="./flows/basic_with_llm",
        # run flow against local data or existing run, only one of data & run can be specified. 
        data="./flows/basic_with_llm/data.jsonl"
    )

    eval_flow = "./flows/eval_basic_with_llm"

    # run the flow with exisiting run
    eval_run = pf.run(
        flow=eval_flow,
        data="./flows/eval_basic_with_llm/data.jsonl",
        run=base_run,
        column_mapping={"groundtruth": "${data.prediction}","prediction": "${run.outputs.output}"},  # map the url field from the data to the url input of the flow
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