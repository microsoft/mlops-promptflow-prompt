"""Shows example how to invoke the flow using different ways."""
import os
import argparse
from promptflow.client import PFClient
from flows.class_plan_and_execute.standard.plan_and_execute import PlanAndExecute
from mlops.common.config_utils import MLOpsConfig


def main():
    """
    Execute class_plan_and_execute using different ways.

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
    flow_config = mlops_config.get_flow_config(flow_name="class_plan_and_execute")
    openai_config = mlops_config.aoai_config

    os.environ["aoai_api_key"] = openai_config["aoai_api_key"]
    os.environ["bing_api_key"] = flow_config["bing_api_key"]
    os.environ["aoai_model_gpt4"] = flow_config["deployment_name_gpt4"]
    os.environ["aoai_model_gpt35"] = flow_config["deployment_name_gpt35"]
    os.environ["aoai_base_url"] = openai_config["aoai_api_base"]
    os.environ["aoai_api_version"] = flow_config["aoai_api_version"]
    os.environ["bing_endpoint"] = flow_config["bing_endpoint"]

    # Run the flow as a basic function call with no tracing
    plan_and_execute = PlanAndExecute(
        planner_system_message_path=flow_config["planner_system_message_path"],
        solver_system_message_path=flow_config["solver_system_message_path"],
    )

    print(
        plan_and_execute(
            question="What was the total box office performance of 'Inception' and 'Interstellar' together?"
        )
    )

    # Run the flow as a PromptFlow flow with tracing on a single row.
    flow_standard_path = flow_config["standard_flow_path"]
    planner_system_message_path = os.path.basename(flow_config["planner_system_message_path"])
    solver_system_message_path = os.path.basename(flow_config["solver_system_message_path"])

    pf = PFClient()
    print(
        pf.test(
            flow=flow_standard_path,
            init={"planner_system_message_path": planner_system_message_path,
                  "solver_system_message_path": solver_system_message_path},
        )
    )

    # Run the flow as a PromptFlow batch on a data frame.
    data_standard_path = flow_config['data_path']
    column_mapping = flow_config['column_mapping']

    run_instance = pf.run(
        flow=flow_standard_path,
        init={"planner_system_message_path": planner_system_message_path,
              "solver_system_message_path": solver_system_message_path},
        data=data_standard_path,
        column_mapping=column_mapping,
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
