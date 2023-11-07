import os
import argparse
from promptflow import PFClient
from promptflow.entities import AzureOpenAIConnection


def main():
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--aoai-connection-name",
        type=str,
        required=True,
        help="connection name in the flow",
    )
    parser.add_argument(
        "--aoai-api-key",
        type=str,
        required=True,
        help="api key to get access to the service",
    )
    parser.add_argument(
        "--aoai-api-base", type=str, required=True, help="base api url of the service"
    )
    parser.add_argument(
        "--aoai-api-type", type=str, default="azure", help="api type (azure as for now)"
    )
    parser.add_argument(
        "--aoai-api-version", type=str, default="2023-07-01-preview", help="api version"
    )
    args = parser.parse_args()

    # PFClient can help manage your runs and connections.
    pf = PFClient()

    try:
        conn_name = args.aoai_connection_name
        conn = pf.connections.get(name=conn_name)
        print("using existing connection")
    except:
        connection = AzureOpenAIConnection(
            name=conn_name,
            api_key=args.aoai_api_key,
            api_base=args.aoai_api_base,
            api_type=args.aoai_api_type,
            api_version=args.aoai_api_version,
        )

        conn = pf.connections.create_or_update(connection)
        print("successfully created connection")


if __name__ == "__main__":
    main()
