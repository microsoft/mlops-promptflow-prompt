""" Flow shared utilities """
from promptflow.entities import Run
from promptflow.azure import PFClient
from azure.identity import DefaultAzureCredential, AzureCliCredential
from promptflow._sdk._constants import RunStatus
from mlops.common.mlflow_tools import generate_experiment_name, generate_run_name


def prepare_and_execute_std_flow(
    subscription_id,
    resource_group_name,
    workspace_name,
    # runtime,
    column_mapping,
    build_id,
    standard_flow_path,
    experiment_name,
    output_file,
    standard_data_path,
):
    """
    Execute a standard flow in Azure ML.

    Parameters:
      subscription_id (string): a subsription id where Azure ML workspace is located
      resource_group (string): a resource group name where Azure ML workspace is located
      workspace_name (string): Azure ML workspace name
      column_mapping (string): mapping rules
      build_id (string): a build id
      standard_flow_path (string): a standard flow folder path
      experiment_name (string): an experiment name
      output_file (string): an optional file name to store run id
      standard_data_path (string): a path to data file in Azure ML notation
    """
    pf = PFClient(
        DefaultAzureCredential(), subscription_id, resource_group_name, workspace_name
    )

    run = Run(
        flow=standard_flow_path,
        data=standard_data_path,
        # runtime=runtime,
        name=generate_run_name(),
        display_name=generate_run_name(),
        column_mapping=column_mapping,
        tags={"build_id": build_id},
    )

    run._experiment_name = generate_experiment_name(experiment_name)

    pipeline_job = pf.runs.create_or_update(run, stream=True)

    if pipeline_job.status == "Completed" or pipeline_job.status == "Finished":  # 4
        print("job completed")
    else:
        raise Exception("Sorry, exiting job with failure..")

    if output_file is not None:
        with open(output_file, "w") as out_file:
            out_file.write(pipeline_job.name)
    print(pipeline_job.name)

def prepare_and_execute_eval_flow(
    subscription_id,
    resource_group_name,
    workspace_name,
    # runtime,
    build_id,
    eval_flow_path,
    experiment_name,
    data_config_path,
    run_id,
    eval_column_mapping,
):
    """
    Execute an evaluation flow in Azure ML.

    Parameters:
      subscription_id (string): a subsription id where Azure ML workspace is located
      resource_group (string): a resource group name where Azure ML workspace is located
      workspace_name (string): Azure ML workspace name
      build_id (string): a build id
      eval_flow_path (string): an evaluation flow folder path
      experiment_name (string): an experiment name
      data_config_path (string): a path to data file in Azure ML notation
      run_id (string): a run id of the standard flow run to evaluate
      eval_column_mapping (string): a mapping between columns in the ground truth and results from standard run
    """
    pf = PFClient(
        DefaultAzureCredential(), subscription_id, resource_group_name, workspace_name
    )

    my_run = pf.runs.get(run_id)

    run = Run(
        flow=eval_flow_path,
        data=data_config_path,
        run=my_run,
        column_mapping=eval_column_mapping,
        # runtime=runtime,
        name=f"{generate_run_name()}_eval",
        display_name=f"{generate_run_name()}_eval",
        tags={"build_id": build_id},
    )
    run._experiment_name = f"{generate_experiment_name(experiment_name)}_eval"

    pipeline_job = pf.runs.create_or_update(run, stream=True)

    if pipeline_job.status == "Completed" or pipeline_job.status == "Finished":
        print(pipeline_job.status)
    else:
        raise Exception("Sorry, exiting job with failure..")



def get_credentials():
    """
        Get Azure CLI tokem.
    """
    credential = AzureCliCredential()

    token = credential.get_token("https://management.azure.com/.default")
    assert token is not None

    return credential

def get_flow_status(pf: PFClient, run_name: str) -> str:
    """
        Get flow status for a given run.

        Parameters:
        pf (PFClient): Promptflow client
        run_name (string): run name
    """
    result = pf.runs.get(run_name)
    status = result.status

    if (
        status == RunStatus.QUEUED
        or status == RunStatus.NOT_STARTED
        or status == RunStatus.PREPARING
        or status == RunStatus.PROVISIONING
        or status == RunStatus.STARTING
        or status == RunStatus.RUNNING
        or status == RunStatus.FINALIZING
    ):
        print(f"Run {run_name} is still running with status {status}.")
        return "IN_PROGRESS"
    elif status == RunStatus.COMPLETED:
        print(f"Run {run_name} completed with status {status}.")
        return "DONE"
    else:
        print(f"Run {run_name} failed with status {status}.")
        return "REJECTED"

def save_run_data(pf: PFClient, run_name: str, filename: str):
    """
        Save run data for a given run to a file.

        Parameters:
        pf (PFClient): Promptflow client
        run_name (string): run name
        filename (string): filename to store the run data
    """
    result = pf.get_details(run_name, all_results = True)
    line_number_column = "inputs.line_number"
    if line_number_column in result.columns:
        result.sort_values(by=line_number_column, ascending=True, inplace=True)
    result.to_csv(filename, index = False)

def get_run_metrics(pf: PFClient, run_name: str) -> dict:
    """
        Run metrics for a given run, returned as dict.

        Parameters:
        pf (PFClient): Promptflow client
        run_name (string): run name
    """
    evaluation_run = pf.runs.get(run_name)
    metrics = pf.get_metrics(evaluation_run)
    metrics["Run"] = evaluation_run.run
    metrics["Data"] = evaluation_run.data.split("/")[-1] if evaluation_run.data else None

    return metrics
