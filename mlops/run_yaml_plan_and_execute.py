"""Shows example how to invoke the flow using different ways."""
import argparse
from promptflow.client import PFClient
from mlops.common.config_utils import MLOpsConfig
from promptflow.client import load_flow
from promptflow.entities import CustomConnection


def main():
    """
    Execute yaml_plan_and_execute using different ways.

    The method uses config.yaml as a source for parameters, and
    it runs the flow in different ways that can be used to test the flow locally.
    """
    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    parser.add_argument("--visualize", default=False, action="store_true")
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environemnt=args.environment_name)
    flow_config = mlops_config.get_flow_config(flow_name="yaml_plan_and_execute")
    openai_config = mlops_config.aoai_config

    # Run the flow as a function.
    flow_standard_path = flow_config["standard_flow_path"]

    connection = CustomConnection(
        name=flow_config["connection_name"],
        secrets={"aoai_api_key": openai_config["aoai_api_key"],
                 "bing_api_key": flow_config["bing_api_key"]},
        configs={"aoai_model_gpt4": flow_config["deployment_name_gpt4"],
                 "aoai_model_gpt35": flow_config["deployment_name_gpt35"],
                 "aoai_base_url": openai_config["aoai_api_base"],
                 "aoai_api_version": flow_config["aoai_api_version"],
                 "bing_endpoint": flow_config["bing_endpoint"]}
    )

    pf = PFClient()
    pf.connections.create_or_update(connection)

    flow = load_flow(flow_standard_path)

    print(flow(
        question="What was the total box office performance of 'Inception' and 'Interstellar' together?")
    )

    # Run the flow as a PromptFlow batch on a data frame.
    data_standard_path = flow_config['data_path']
    column_mapping = flow_config['column_mapping']

    run_instance = pf.run(
        flow=flow_standard_path,
        data=data_standard_path,
        column_mapping=column_mapping
    )

    pf.stream(run_instance)

    if run_instance.status == "Completed" or run_instance.status == "Finished":
        print("Experiment has been completed")
    else:
        raise Exception("Sorry, exiting job with failure..")

    print(run_instance.name)
    if args.visualize is True:
        pf.runs.visualize(run_instance)


if __name__ == "__main__":
    main()
