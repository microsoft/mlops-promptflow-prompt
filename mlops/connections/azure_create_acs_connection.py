"""This module helps to create a connection in Azure ML to Azure Cognitive Search service."""
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AzureAIServicesConnection
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from mlops.common.config_utils import MLOpsConfig


def main():
    """Create an Azure ML connection to Azure Cognitive Service using command line parameters."""
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--acs-connection-name",
        type=str,
        required=True,
        help="connection name in the flow",
    )
    args = parser.parse_args()
    mlops_config = MLOpsConfig()
    aistudio_config = mlops_config.aistudio_config
    acs_config = mlops_config.acs_config

    # MLClient can help manage your runs and connections.
    client = MLClient(
        DefaultAzureCredential(),
        aistudio_config["subscription_id"],
        aistudio_config["resource_group_name"],
        aistudio_config["project_name"],
    )

    try:
        conn_name = args.acs_connection_name
        result = client.connections.get(name=conn_name)
        print("using existing connection")
    except HttpResponseError:
        print("connection not found. creating a new one.")
        connection = AzureAIServicesConnection(
            name=conn_name,
            api_key=acs_config["acs_api_key"],
            endpoint=acs_config["acs_api_base"],
        )
        result = client.connections.create_or_update(connection)
        print("connection has been created")

    return result


if __name__ == "__main__":
    main()
