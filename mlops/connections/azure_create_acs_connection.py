"""This module helps to create a connection in Azure ML to Azure Cognitive Search service."""
import argparse
import requests
import json
from promptflow.azure import PFClient
from azure.identity import DefaultAzureCredential
from promptflow.azure._restclient.flow_service_caller import FlowRequestException


def main():
    """Create an Azure ML connection to Azure Cognitive Service using command line parameters."""
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--acs-connection-name",
        type=str,
        required=True,
        help="connection name in the flow",
    )
    parser.add_argument(
        "--acs-api-key",
        type=str,
        required=True,
        help="api key to get access to the service",
    )
    parser.add_argument(
        "--acs-api-base", type=str, required=True, help="base api url of the service"
    )
    parser.add_argument(
        "--acs-api-version", type=str, default="2023-07-01-preview", help="api version"
    )
    parser.add_argument(
        "--subscription-id",
        type=str,
        required=True,
        help="subscription id where Azure ML workspace is located",
    )
    parser.add_argument(
        "--resource-group",
        type=str,
        required=True,
        help="resource group name where Azure ML workspace is located",
    )
    parser.add_argument(
        "--workspace-name", type=str, required=True, help="Azure ML Workspace name"
    )
    args = parser.parse_args()

    # PFClient can help manage your runs and connections.
    pf = PFClient(
        DefaultAzureCredential(),
        args.subscription_id,
        args.resource_group,
        args.workspace_name,
    )

    try:
        conn_name = args.aoai_connection_name
        pf._connections.get(name=conn_name)
        print("using existing connection")
    except FlowRequestException:
        url = f"https://management.azure.com/subscriptions/{args.subscription_id}/" \
            f"resourcegroups/{args.resource_group}/providers/Microsoft.MachineLearningServices/" \
            f"workspaces/{args.workspace_name}/connections/{args.acs_connection_name}?" \
            f"api-version=2023-04-01-preview"
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
                    "category": "CognitiveSearch",
                    "target": args.acs_api_base,
                    "authType": "ApiKey",
                    "credentials": {
                        "key": args.acs_api_key,
                    },
                    "metadata": {"ApiVersion": args.acs_api_version},
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
