"""Shows example how to invoke the flow using different ways."""
import argparse
from promptflow.client import PFClient
from mlops.common.config_utils import MLOpsConfig
from promptflow.client import load_flow
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from flows.chat_with_pdf.evaluate.flow_wrapper import ChatWithPdfFlowWrapper


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
    parser.add_argument("--visualize", default=False, action="store_true")
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environemnt=args.environment_name)
    flow_config = mlops_config.get_flow_config(flow_name="chat_with_pdf")

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

    pf = PFClient()
    pf.connections.create_or_update(connection)

    flow = load_flow(flow_standard_path)
    flow.context = FlowContext(
        connections={"setup_env": {"connection": connection}},
        overrides={
            "inputs.config.default":
            {
                "EMBEDDING_MODEL_DEPLOYMENT_NAME": "text-embedding-ada-002",
                "CHAT_MODEL_DEPLOYMENT_NAME": "gpt-35-turbo",
                "PROMPT_TOKEN_LIMIT": 1900,
                "MAX_COMPLETION_TOKENS": 1024,
                "VERBOSE": "true",
                "CHUNK_SIZE": 512,
                "CHUNK_OVERLAP": 64,
            }
        }
    )

    print(flow(pdf_url="https://arxiv.org/pdf/1810.04805.pdf", question="What is BERT?"))

    # Run the flow as a PromptFlow batch on a data frame.
    data_standard_path = flow_config['data_path']
    column_mapping = flow_config['column_mapping']

    flow_obj = ChatWithPdfFlowWrapper(
        flow_standard_path=flow_standard_path,
        connection_name=flow_config,
        openai_config=openai_config
    )

    run_instance = pf.run(
        flow=flow_obj,
        data=data_standard_path,
        column_mapping=column_mapping
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