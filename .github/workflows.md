# GitHub Workflows

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
  - [Pull Requests](#pull-requests)
  - [Continuous Integration](#continuous-integration)
- [GitHub Secrets](#github-secrets)
- [Azure Resources](#azure-resources)

## Overview

This document provides a high level description of the GitHub Workflows and Actions implemented in this directory, as well as the prerequisites for successfully running the Workflows.

There are two main workflows for each flow. One runs on pull requests and the other is for continuous integration which runs when code is pushed into the `main` branch.

The workflows in this repo are based on the Azure Pipelines which are located in the[.azure-pipelines](../.azure-pipelines) directory.

### Pull Requests

`*_pr_dev_workflow` runs for each pull request into the `development` branch.
It builds and executes the flow locally on a Github build machine. After execution, the run details can be viewed in the **Jobs** section of Azure AI Machine Learning Studio (AML).

### Continuous Integration

`*_ci_dev_workflow` runs for each push into the `development` branch
It runs the flow and then creates and then creates a new version of the model for that flow in AML. The model can be viewed in the **Models** section of AML. It then takes that model and deploys it to a real-time endpoint that can be used for testing. That endpoint and the logs associated to it can be viewed in the **Endpoints** section of AML.

## GitHub Secrets

The following secrets are required in order to run the Workflows successfully:

- `SUBSCRIPTION_ID` : The ID of the Azure subscription resources should be deployed to.
- `AZURE_CREDENTIALS` : The Service Principal credentials to authenticate with the Azure subscription. Follow this [documentation](<https://learn.microsoft.com/en-us/cli/azure/ad/sp?view=azure-cli-latest#az-ad-sp-create-for-rbac()>) to create the expected JSON object.
- `AOAI_API_KEY` : The API Key to authenticate wit the Azure Open AI instance used in the workflows.

## Azure Resources

The PR and CI workflows are implemented with the assumption that the following resources exist in the target Azure subscription.

- A resource group named `sbaydachairg`. If resource group is not available, update `RESOURCE_GROUP_NAME` in [model config](/config/model_config.json) to the name of resource group which will be used.

- An Azure Machine Learning (AML) instance named `sbaydachmlwrksp` in the resource group. If this name is not used, update the `WORKSPACE_NAME` in the model config to the appropriate value.

- An Azure Open AI instance with the URL `REPLACE_NAME_HERE`. If this URL is not used, replace all instances with the correct value. This instance should have at least one embedding model and one chat model deployed to it.

  - Create a [connection in Promptflow](https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/get-started-prompt-flow?view=azureml-api-2#connection) for Azure Open AI and it should be named `azure_open_ai_connection`.
    - Remove the trailing slash from the base url

- Within the AML workspace, an endpoint called `named-entity`. This endpoint should exist prior to the initial CI workflow run, following these [instructions](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints). It is important to ensure the endpoint has the `Azure ML Data Scientist` role assigned in order to execute any PromptFlow code.
  - To add this role to the endpoint:
    - Navigate to Azure ML Workspace and select access control
    - Select `Add role assignment`
    - Select `AzureML Data Scientist` under roles
    - In the members tab, select `managed identity`
    - When adding members, select the endpoint and then complete the role assignment.
