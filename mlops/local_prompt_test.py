"""This is MLOps utility module to execute evaluation flow locally using a single line of data."""
import argparse
from promptflow.client import PFClient
from mlops.common.config_utils import MLOpsConfig


def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given standard flow locally on a single line of data."""
    flow_standard_path = ""

    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--config_name",
        type=str,
        required=True,
        help="prompt_flow_config_name from config.yaml",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environemnt=args.environment_name)
    flow_config = mlops_config.get_flow_config(flow_name=args.config_name)

    flow_standard_path = flow_config['standard_flow_path']

    pf_client = PFClient()

    # Using default input
    # inputs = {"<flow_input_name>": "<flow_input_value>"}  # The inputs of the flow.

    flow_result = pf_client.test(flow=flow_standard_path)
    print(f"Flow outputs: {flow_result}")


if __name__ == "__main__":
    main()
