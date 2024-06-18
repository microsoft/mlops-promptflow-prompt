"""Shows example how to invoke the flow using different ways."""
import argparse
from promptflow.client import PFClient
from mlops.common.config_utils import MLOpsConfig
from promptflow.client import load_flow
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from mlops.common.trace_destination import get_destination_url


def main():
    """
    Execute function_basic_flow using different ways.

    The method uses config.yaml as a source for parameters, and
    it runs the flow in different ways that can be used to test the flow locally.
    """
    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    parser.add_argument("--deploy_traces", default=False, action="store_true")
    parser.add_argument("--visualize", default=False, action="store_true")
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environment=args.environment_name)
    flow_config = mlops_config.get_flow_config(flow_name="yaml_basic_flow")

    aoai_deployment = flow_config["deployment_name"]

    openai_config = mlops_config.aoai_config

    # Run the flow as a function.
    flow_standard_path = flow_config["standard_flow_path"]

    connection = AzureOpenAIConnection(
        name=flow_config["connection_name"],
        api_key=openai_config["aoai_api_key"],
        api_base=openai_config["aoai_api_base"],
        api_type="azure",
        api_version=openai_config["aoai_api_version"],
    )

    if args.deploy_traces is True:
        trace_destination = get_destination_url(mlops_config.aistudio_config)
    else:
        trace_destination = None
    pf = PFClient(config={"trace.destination": trace_destination})

    pf.connections.create_or_update(connection)

    flow = load_flow(flow_standard_path)
    flow.context = FlowContext(
        overrides={"nodes.NER_LLM.inputs.deployment_name": aoai_deployment},
        connections={"NER_LLM": {"connection": connection}},
    )

    print(
        flow(
            entity_type="job title",
            text="The CEO and CFO are discussing the financial forecast for the next quarter.",
        )
    )

    # Run the flow as a PromptFlow batch on a data frame.
    data_standard_path = flow_config["data_path"]
    column_mapping = flow_config["column_mapping"]

    run_instance = pf.run(
        flow=flow_standard_path,
        data=data_standard_path,
        column_mapping=column_mapping,
        connections={
            "NER_LLM": {
                "connection": flow_config["connection_name"],
                "deployment_name": aoai_deployment,
            }
        },
    )

    pf.stream(run_instance)

    if run_instance.status == "Completed" or run_instance.status == "Finished":
        print("Experiment has been completed")
    else:
        raise Exception("Sorry, exiting job with failure..")

    print(run_instance.name)
    if args.visualize is True:
        pf.runs.visualize(run_instance)


if __name__ == "__main__":
    main()
