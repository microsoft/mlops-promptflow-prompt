"""This module implements provisioning of Azure ML online endpoint."""
import argparse
from azure.ai.resources.client import AIClient

# from azure.ai.generative.entities.deployment import Deployment
# from azure.ai.generative.entities.models import PromptflowModel
from azure.identity import DefaultAzureCredential
from mlops.common.config_utils import MLOpsConfig


def provision_endpoint(
    subscription_id, resource_group_name, project_name, endpoint_name, flow_path
):
    """
    Create a managed Azure ML online endpoint.

    Parameters:
      subscription_id (string): a subsription id where AI Studio is located
      resource_group (string): a resource group name where AI Studio is located
      project_name (string): AI Studio Project name
      endpoint_name (string): Service deployment name in AI Studio
      flow_path (string): PromptFlow path to deploy
    """
    credential = DefaultAzureCredential()

    AIClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        project_name=project_name,
    )

    # Define your deployment
    # deployment = Deployment(
    #     name=endpoint_name,
    #     model=PromptflowModel(path=flow_path),
    #     instance_type="STANDARD_DS2_V2"
    # )

    # Deploy the promptflow
    # deployment = client.deployments.create_or_update(deployment)


def main():
    """Read command line arguments and invoke provision_endpoint to create AI Studio online endpoint."""
    parser = argparse.ArgumentParser("provision_endpoints")
    parser.add_argument("--model_type", type=str, help="PF flow name", required=True)
    parser.add_argument(
        "--environment_name",
        type=str,
        help="environment name (e.g. dev, test, prod)",
        required=True,
    )
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environemnt=args.environment_name)
    aistudio_config = mlops_config.aistudio_config
    flow_config = mlops_config.get_flow_config(flow_name=args.model_type)

    flow_standard_path = flow_config["standard_flow_path"]

    deployment_config = mlops_config.get_deployment_config(args.model_type, "online")

    provision_endpoint(
        aistudio_config["subscription_id"],
        aistudio_config["resource_group_name"],
        aistudio_config["project_name"],
        deployment_config["endpoint_name"],
        flow_standard_path,
    )


if __name__ == "__main__":
    main()
