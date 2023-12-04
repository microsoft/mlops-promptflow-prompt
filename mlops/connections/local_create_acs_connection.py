"""This module helps to create a local connection to Azure Cognitive Search service."""
import argparse
from promptflow import PFClient
from promptflow.entities import CognitiveSearchConnection
from promptflow._sdk._errors import ConnectionNotFoundError


def main():
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
        "--acs-api-base", type=str, required=True, help="base uri of the service"
    )
    parser.add_argument(
        "--acs-api-version", type=str, default="2023-07-01-preview", help="api version"
    )
    args = parser.parse_args()

    # PFClient can help manage your runs and connections.
    pf = PFClient()

    try:
        conn_name = args.acs_connection_name
        pf.connections.get(name=conn_name)
        print("using existing connection")
    except ConnectionNotFoundError:
        connection = CognitiveSearchConnection(
            name=conn_name,
            api_key=args.acs_api_key,
            api_base=args.acs_api_base,
            api_version=args.acs_api_version,
        )

        pf.connections.create_or_update(connection)
        print("successfully created connection")


if __name__ == "__main__":
    main()
