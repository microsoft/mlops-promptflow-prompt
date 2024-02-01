"""This module helps to create a local connection to Azure Open AI service."""
import argparse
from promptflow import PFClient
from promptflow.entities import AzureOpenAIConnection
from promptflow._sdk._errors import ConnectionNotFoundError
from shared.config_utils import load_yaml_config


def main():
    """Create a local connection to Azure Open AI using command line parameters."""
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--aoai-connection-name",
        type=str,
        required=True,
        help="connection name in the flow",
    )

    args = parser.parse_args()

    # Read configuration
    mlops_config = load_yaml_config()
    aoai_config = mlops_config.aoai_config

    # PFClient can help manage your runs and connections.
    pf = PFClient()

    try:
        conn_name = args.aoai_connection_name
        pf.connections.get(name=conn_name)
        print("using existing connection")
    except ConnectionNotFoundError:
        connection = AzureOpenAIConnection(
            name=conn_name,
            api_key=aoai_config['aoai_api_key'],
            api_base=aoai_config['aoai_api_base'],
            api_type=aoai_config['aoai_api_type'],
            api_version=aoai_config['aoai_api_version'],
        )

        pf.connections.create_or_update(connection)
        print("successfully created connection")


if __name__ == "__main__":
    main()
