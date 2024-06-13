"""Shows example how to invoke the flow using different ways."""
import argparse
from promptflow.client import PFClient
from flows.class_basic_flow.standard.extract_entities import EntityExtraction
from mlops.common.config_utils import MLOpsConfig
from promptflow.entities import AzureOpenAIConnection
from promptflow.core import AzureOpenAIModelConfiguration


def main():
    """
    Execute class_basic_flow using different ways.

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
    flow_config = mlops_config.get_flow_config(flow_name="class_basic_flow")

    aoai_deployment = flow_config["deployment_name"]

    openai_config = mlops_config.aoai_config

    connection = AzureOpenAIConnection(
        name=flow_config["connection_name"],
        api_key=openai_config["aoai_api_key"],
        api_base=openai_config["aoai_api_base"],
        api_type="azure",
        api_version=openai_config["aoai_api_version"],
    )

    pf = PFClient()
    pf.connections.create_or_update(connection)

    # create the model config to be used in below flow calls
    config = AzureOpenAIModelConfiguration(
        connection=flow_config["connection_name"], azure_deployment=aoai_deployment
    )

    # Run the flow as a basic function call with no tracing
    obj_chat = EntityExtraction(model_config=config)

    print(
        obj_chat(
            entity_type="job title",
            text="The CEO and CFO are discussing the financial forecast for the next quarter.",
        )
    )

    # Run the flow as a PromptFlow flow with tracing on a single row.
    flow_standard_path = flow_config["standard_flow_path"]

    pf = PFClient()
    print(pf.test(flow=flow_standard_path, init={"model_config": config}))

    # Run the flow as a PromptFlow batch on a data frame.
    data_standard_path = flow_config["data_path"]
    column_mapping = flow_config["column_mapping"]

    run_instance = pf.run(
        flow=flow_standard_path,
        data=data_standard_path,
        column_mapping=column_mapping,
        init={"model_config": config},
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
