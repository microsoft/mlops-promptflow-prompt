"""Shows example how to invoke the flow using different ways in Azure."""
import argparse
from promptflow.azure import PFClient
from mlops.common.config_utils import MLOpsConfig
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
import logging


def main():
    """
    Execute function_basic_flow using different ways.

    The method uses config.yaml as a source for parameters, and
    it runs the flow in different ways that can be used to test the flow in Azure.
    """
    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    args = parser.parse_args()
    mlops_config = MLOpsConfig(environment=args.environment_name)
    flow_config = mlops_config.get_flow_config(flow_name="yaml_basic_flow")
    aoai_deployment = flow_config["deployment_name"]
    aistudio_config = mlops_config.aistudio_config
    flow_standard_path = flow_config["standard_flow_path"]

    # Azure OpenAI Connection check (aoai):
    credential = DefaultAzureCredential()
    try:
        ml_client = MLClient(
            subscription_id=aistudio_config["subscription_id"],
            resource_group_name=aistudio_config["resource_group_name"],
            workspace_name=aistudio_config["project_name"],
            credential=credential,
        )
        created_connection = ml_client.connections.get(flow_config["connection_name"])
        logging.debug(f"connection found: {created_connection}")
    except Exception as e:
        logging.debug(f"connection not found: {e}")
        raise Exception("Azure OpenAI configuration connection does not exist.")

    pf = PFClient(
        credential,
        aistudio_config["subscription_id"],
        aistudio_config["resource_group_name"],
        aistudio_config["project_name"],
    )

    # Run the flow as a PromptFlow batch on a data frame.
    data_standard_path = flow_config["data_path"]
    column_mapping = flow_config["column_mapping"]
    run_instance = pf.run(
        flow=flow_standard_path,
        data=data_standard_path,
        column_mapping=column_mapping,
        connections={
            "NER_LLM": {
                "connection": flow_config["connection_name"],
                "deployment_name": aoai_deployment,
            }
        },
        stream=True,
    )

    print(f"Current status is: {run_instance.status}")

    if run_instance.status == "Completed" or run_instance.status == "Finished":
        print("Experiment has been completed")
    elif run_instance.status == "Preparing":
        print("Preparing flow run for the experiment")
    elif run_instance.status == "NotStarted":
        print("Flow run for the experiment not started")
    else:
        raise Exception("Sorry, exiting job with failure..")
    print(run_instance.name)


if __name__ == "__main__":
    main()
