"""This module helps to create a local connection to Azure Cognitive Search service."""
import argparse
from promptflow import PFClient
from promptflow.entities import CognitiveSearchConnection
from promptflow._sdk._errors import ConnectionNotFoundError
from shared.config_utils import MLOpsConfig


def main():
    """Create a local connection to Azure Cognitive Service using command line parameters."""
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--acs-connection-name",
        type=str,
        required=True,
        help="connection name in the flow",
    )
    args = parser.parse_args()

    # Read configuration
    mlops_config = MLOpsConfig()
    acs_config = mlops_config.acs_config

    # PFClient can help manage your runs and connections.
    pf = PFClient()

    try:
        conn_name = args.acs_connection_name
        pf.connections.get(name=conn_name)
        print("using existing connection")
    except ConnectionNotFoundError:
        connection = CognitiveSearchConnection(
            name=conn_name,
            api_key=acs_config['acs_api_key'],
            api_base=acs_config['acs_api_base'],
            api_version=acs_config['acs_api_version'],
        )

        pf.connections.create_or_update(connection)
        print("successfully created connection")


if __name__ == "__main__":
    main()
