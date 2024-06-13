"""Shows example how to invoke the flow using different ways."""
import os
import argparse
from promptflow.client import PFClient
from flows.function_basic_flow.standard import extract_entities
from mlops.common.config_utils import MLOpsConfig


def main():
    """
    Execute function_basic_flow using different ways.

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
    flow_config = mlops_config.get_flow_config(flow_name="function_basic_flow")

    aoai_deployment = flow_config["deployment_name"]

    openai_config = mlops_config.aoai_config

    os.environ["AZURE_OPENAI_API_KEY"] = openai_config["aoai_api_key"]
    os.environ["AZURE_OPENAI_API_VERSION"] = openai_config["aoai_api_version"]
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = aoai_deployment
    os.environ["AZURE_OPENAI_ENDPOINT"] = openai_config["aoai_api_base"]

    # Run the flow as a basic function call with no tracing
    print(
        extract_entities.extract_entity(
            "job title",
            "The CEO and CFO are discussing the financial forecast for the next quarter.",
        )
    )

    # Run the flow as a PromptFlow flow with tracing on a single row.
    flow_standard_path = flow_config["standard_flow_path"]

    pf = PFClient()
    print(pf.test(flow=flow_standard_path))

    # Run the flow as a PromptFlow batch on a data frame.
    data_standard_path = flow_config["data_path"]
    column_mapping = flow_config["column_mapping"]

    run_instance = pf.run(
        flow=flow_standard_path,
        data=data_standard_path,
        column_mapping=column_mapping,
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
