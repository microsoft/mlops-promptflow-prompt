"""This module helps to create a connection in Azure ML to Azure Open AI service."""
import argparse
import json
import requests
from promptflow.azure import PFClient
from azure.identity import DefaultAzureCredential
from promptflow.azure._restclient.flow_service_caller import FlowRequestException
from shared.config_utils import load_yaml_config


def main():
    """Create an Azure ML connection to Azure Open AI using command line parameters."""
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--aoai-connection-name",
        type=str,
        required=True,
        help="connection name in the flow",
    )
    args = parser.parse_args()

    # Read configuratuin
    mlops_config = load_yaml_config()
    aml_config = mlops_config.aml_config
    aoai_config = mlops_config.aoai_config

    # PFClient can help manage your runs and connections.
    pf = PFClient(
        DefaultAzureCredential(),
        aml_config['subscription_id'],
        aml_config['resource_group_name'],
        aml_config['workspace_name'],
    )

    try:
        conn_name = args.aoai_connection_name
        pf._connections.get(name=conn_name)
        print("using existing connection")
    except FlowRequestException:
        url = f"https://management.azure.com/subscriptions/{aml_config['subscription_id']}/" \
            f"resourcegroups/{aml_config['resource_group_name']}/providers/Microsoft.MachineLearningServices/" \
            f"workspaces/{aml_config['workspace_name']}/connections/{args.aoai_connection_name}" \
            f"?api-version=2023-04-01-preview"
        token = (
            DefaultAzureCredential()
            .get_token("https://management.azure.com/.default")
            .token
        )
        header = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }

        data = json.dumps(
            {
                "properties": {
                    "category": "AzureOpenAI",
                    "target": aoai_config['aoai_api_base'],
                    "authType": "ApiKey",
                    "credentials": {
                        "key": aoai_config['aoai_api_key'],
                    },
                    "metadata": {
                        "ApiType": aoai_config['aoai_api_type'],
                        "ApiVersion": aoai_config['aoai_api_version'],
                    },
                }
            }
        )

        with requests.Session() as session:
            response = session.put(url, data=data, headers=header)
            # Raise an exception if the response contains an HTTP error status code
            response.raise_for_status()

        print(response.json())


if __name__ == "__main__":
    main()
