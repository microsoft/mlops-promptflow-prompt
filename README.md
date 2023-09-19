# MLOps for PromptFlow Workloads

The goal of this repo is to show how to implement MLOps process for Open AI workloads using PromptFlow SDK and code-first approach.

The repository contains all needed components to help developing and deploying one or more PromptFlow pipelines starting from local execution and up to online endpoint deployment.

## Structure of the repository

In the repository you can find the following folders:

- **.azure-pipelines**: as for now, we are supporting Azure DevOps as CI/CD orchestrator. The folder contains all related yaml files that allow you to create PR and Dev Builds (as described later in the doc).
- **config**: this folder contains a configuration file to configure one or more PromptFlow models in different environments. The configuration file is related to CI/CD and it can be treated as a component of the DevOps pipeline. It's placed into a separate folder to make it available for all supported DevOps systems (Azure DevOps only as for now).
- **flows**: PromptFlow flows and related data files should be stored here. The repository includes one PromptFlow model as an example, but it contains two flows/pipelines to solve the task (the model itself) and evaluate results (useful at experimentation and development stages).
- **mlops**: the folder contains code and configuration files to support MLOps process. It includes some common files and files that are specific to a model.
- **test**: unit-tests should be located here.

## Azure Open AI Resource

In order to use flows from this template you need to deploy GPT Turbo 3.5 model in your cloud environment.

**Note**. PromtFlow SDK at this stage doesn't allow us to assign connection name and deployment name dynamically (at least, during the deployment). So, we would recommend to use `gpt-35-turbo` as a deployment name and `aoai` as a connection name (connection name required if you execute PF flow in the cloud). If you pick any different name, replace above values to your across the template.

## MLFlow Logging

We are using MLFlow to log experiment results. By default we are using MLFlow deployment in Azure ML Workspace, but it can be any other MLFlow deployment.

If you would like to see MLFlow results in Azure ML, you need to provide the following parameters:

- **SUBSCRIPTION_ID** (.env file): a subscription id where the Azure ML Workspace is located.
- **RESOURCE_GROUP_NAME** (config/model_config.json): a resource group name where the workspace is located.
- **WORKSPACE_NAME** (config/model_config.json): a workspace name, where you would like to log experiments.

## Local Execution

PromptFlow SDK allows us to execute flows on a local computer. To execute the flow that we are providing as an example, you just need to copy `.env.sample` and rename it into `.env`. The file contains few parameters, but you need to provide just two of them:

- **AOAI_API_KEY**: Azure Open AI key to get access.
- **AOAI_API_BASE**: a base uri for your Azure Open AI endpoint (`https://<your service name>.openai.azure.com/`).

Once it's done, you need to make sure that you have an environment to execute PromptFlow locally. In [the following document](conda_environment.md) we are explaining how to create a local `conda` environment.

All scripts are designed in a way to be executed from the root project folder. You need to create a connection (local one) first executing the following command:

```bash
python -m mlops.local_create_aoai_connection
```

If everything works fine, you can test the flow using the following commands.

Test the flow on a single data entry (default one):

```bash
python -m mlops.local_prompt_test --config_name named_entity_recognition --environment_name pr
```

Run the flow  using a data file, and display results in the browser:

```bash
python -m mlops.local_prompt_pipeline --config_name named_entity_recognition --environment_name pr
```

Run the flow alongside with evaluation:

```bash
python -m mlops.named_entity_recognition.local_prompt_eval
```

## Azure DevOps Setup

### Setup resources in Azure

Prior to configure Azure DevOps you need to make sure that `aoai` (or your favorite name, but look at notes above) connection has been created for your deployment in Azure Open AI. The current version of the SDK doesn't allow us to create the connection automatically.

Use PromptFlow tab in Azure ML Studio to create a runtime that you will use to execute the flows. We would recommend to use Managed Online Deployment Runtime. Once the endpoint has been created, you need to assign permissions to it according to [this document](https://learn.microsoft.com/en-ca/azure/machine-learning/prompt-flow/how-to-deploy-for-real-time-inference?view=azureml-api-2#grant-permissions-to-the-endpoint).

### Branches

We would recommend to use **development** branch as the primary branch to do development. If you pick any other branch name, you will need to modify `named_entity_recognition_ci_dev_pipeline.yml` and `named_entity_recognition_pr_dev_pipeline.yml`. You need to change `development` at the top to your preferred name.

### Modify configuration

At least three parameters must be modified in `config/model_config.json`:

- **RUNTIME_NAME**: Managed Online Endpoint Runtime name from the previous step.
- **RESOURCE_GROUP_NAME**: Azure ML Resource Group name.
- **WORKSPACE_NAME**: Azure ML Workspace name.

### Service Connection

Create a service connection in Azure DevOps. You can use [this document](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) as a reference. Use Azure Resource Manager as a type of the service connection.

### Variable Group

Create a new variable group `mlops_platform_dev_vg` with the following variables:

- AZURE_RM_SVC_CONNECTION: the service connection name from the previous step.

Information about variable groups in Azure DevOps can be found in [this document](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=classic).

### Create Builds

Create two Azure Pipelines. Both Azure Pipelines should be created based on existing YAML files. The first one is based on the [named_entity_recognition_pr_dev_pipeline.yml], and it helps to maintain code quality for all PRs. The second Azure Pipeline is based on [named_entity_recognition_ci_dev_pipeline.yml](../devops/pipeline/ci_dev_pipeline.yml) that should be executed automatically once new PR has been merged into the **development** branch. The main idea of this pipeline is to execute training on the full dataset, evaluate results and publish the PromptFlow model as a service into the development environment. The second pipeline can be replicated to make deployment into qa and production environments later.

Run the pipelines one by one to make sure that they work fine. This step completes the setup.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
