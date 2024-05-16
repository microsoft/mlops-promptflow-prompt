"""This is MLOps utility module to execute evaluation flow locally."""
import argparse
from promptflow.client import PFClient
from mlops.common.config_utils import MLOpsConfig


def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given evaluation flow locally."""
    flow_eval_path = ""
    data_eval_path = ""
    eval_column_mapping = ""

    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--config_name",
        type=str,
        required=True,
        help="prompt_flow_config_name from config.yaml",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    parser.add_argument(
        "--run_id", type=str, required=True, help="Rund ID of a run to evaluate"
    )
    args = parser.parse_args()

    mlconfig = MLOpsConfig(environemnt=args.environment_name)
    flow_config = mlconfig.get_flow_config(flow_name=args.config_name)

    flow_eval_path = flow_config['evaluation_flow_path']
    data_eval_path = flow_config['eval_data_path']
    eval_column_mapping = flow_config['eval_column_mapping']

    # Get a pf client to manage runs
    pf = PFClient()

    base_run = pf.runs.get(args.run_id)

    # run the flow with exisiting run
    run_instance = pf.run(
        flow=flow_eval_path,
        data=data_eval_path,
        run=base_run,
        column_mapping=eval_column_mapping,  # map the url field from the data to the url input of the flow
    )

    # stream the run until it's finished
    pf.stream(run_instance)

    if run_instance.status == "Completed" or run_instance.status == "Finished":
        print("Experiment has been completed")
    else:
        raise Exception("Sorry, exiting job with failure..")


if __name__ == "__main__":
    main()
