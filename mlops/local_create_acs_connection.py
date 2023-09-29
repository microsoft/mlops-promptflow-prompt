import os
import argparse
from promptflow import PFClient
from promptflow.entities import CognitiveSearchConnection


def main():
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument("--acs-connection-name", type=str, required=True, help="")
    parser.add_argument("--acs-api-key", type=str, required=True, help="")
    parser.add_argument("--acs-api-base", type=str, required=True, help="")
    parser.add_argument("--acs-api-version", type=str, required=True, help="")
    args = parser.parse_args()

    # PFClient can help manage your runs and connections.
    pf = PFClient()

    try:
        conn_name = args.acs_connection_name
        conn = pf.connections.get(name=conn_name)
        print("using existing connection")
    except:
        connection = CognitiveSearchConnection(
            name=conn_name,
            api_key=args.acs_api_key,
            api_base=args.acs_api_base,
            api_version=args.acs_api_version,
        )

        conn = pf.connections.create_or_update(connection)
        print("successfully created connection")


if __name__ == '__main__':
    main()
