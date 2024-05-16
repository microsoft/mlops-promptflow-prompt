"""This is MLOps utility module to execute standard flow locally."""
import argparse
from promptflow.client import PFClient
from mlops.common.config_utils import MLOpsConfig


def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given standard flow locally."""
    flow_standard_path = ""
    data_standard_path = ""
    column_mapping = ""

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
    parser.add_argument("--visualize", default=False, action="store_true")
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run ids"
    )
    args = parser.parse_args()

    mlconfig = MLOpsConfig(environemnt=args.environment_name)
    flow_config = mlconfig.get_flow_config(flow_name=args.config_name)

    flow_standard_path = flow_config['standard_flow_path']
    data_standard_path = flow_config['data_path']
    column_mapping = flow_config['column_mapping']

    # Get a pf client to manage runs
    pf = PFClient()

    run_instance = pf.run(
        flow=flow_standard_path,
        data=data_standard_path,
        column_mapping=column_mapping,
    )

    pf.stream(run_instance)

    if run_instance.status == "Completed" or run_instance.status == "Finished":
        print("Experiment has been completed")
    else:
        raise Exception("Sorry, exiting job with failure..")

    if args.output_file is not None:
        with open(args.output_file, "w") as out_file:
            out_file.write(run_instance.name)

    print(run_instance.name)
    if args.visualize is True:
        pf.runs.visualize(run_instance)


if __name__ == "__main__":
    main()
