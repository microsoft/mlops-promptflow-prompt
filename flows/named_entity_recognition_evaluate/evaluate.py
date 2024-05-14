import argparse
from azure.ai.generative.evaluate import evaluate
from mlops.common.config_utils import MLOpsConfig


def main():
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="named_entity_recognition for example",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="pr, dev or any other supported environment",
    )

    args = parser.parse_args()

    mlconfig = MLOpsConfig(environemnt=args.environment_name)
    aml_config = mlconfig.aml_config
    flow_config = mlconfig.get_flow_config(flow_name=args.model_name)

    


if __name__ == "__main__":
    main()
