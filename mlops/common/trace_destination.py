"""Utility method to generate url for trace redirection."""


def get_destination_url(project_scope: dict) -> str:
    """Generate uri based on a dictionary from config."""
    subscription_id = project_scope["subscription_id"]
    resource_group_name = project_scope["resource_group_name"]
    workspace_name = project_scope["project_name"]

    trace_destination = (
        f"azureml://subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"
    )

    return trace_destination
