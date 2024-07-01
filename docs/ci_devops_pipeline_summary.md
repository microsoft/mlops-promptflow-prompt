# CI Pipeline Summary

The CI pipeline `basic_flows_ci.yml` is designed to automate the testing, evaluation, and deployment processes for a project with multiple flows:class_basic_flow, yaml_basic_flow, and function_basic_flow. 
The pipeline covers evaluation for different flows and supports multiple deployment targets, including Online Endpoint, Azure Functions, and AKS. 

The pipeline is triggered on pushes to the `development` branch or when specific paths introduce changes:
- '.github/**'
- 'flows/function_basic_flow/**'
- 'flows/class_basic_flow/**'
- 'flows/yaml_basic_flow/**'
- 'src/basic_func_impl/**'
- 'src/basic_flow_fastapi_app/**'

## Description of CI Pipeline

The pipeline is triggered by changes pushed to the `development` branch, specifically targeting paths related to GitHub workflows, and various components of the project including function, class, YAML flows, Azure Functions, and the FastAPI application.

## **Step 1. Setup Environment variables**
The pipeline uses Python 3.9 and sets environment variables for project configuration, including the project name, resource group name, and Docker image name.

## **Step 2. Job**:
   - **run-evaluation-full**: this job checks out the code, sets up Python, exports secrets, and configures the DevOps agent. It then executes evaluation pipelines for function, class, and YAML flows, using credentials for Azure services.

   - **run-online-deployment**: dependent on the completion of the evaluation job, this job deploys an online endpoint for the function flow using Azure Functions.

   - **run-function-deployment**: dependent on the completion of the evaluation job, it prepares and deploys Azure Functions for all flows by compressing function files and deploying them to Azure.

   - **run-aks-deployment**: this build includes steps for logging into ACR, building the Docker image, connecting to AKS, setting up kubectl, creating secrets, deploying an OTel collector, and finally deploying the application to AKS.

   - **Step: Create Secrets** The Azure Kubernetes deployment for a FastAPI application named `basic-flow-app` is defined within `deployment.yaml`configuration file. Service named `basic-flow-app-service` is created within the `basic-flow-app` namespace. This service is of type LoadBalancer, listens on port 8080. Moreover, it defines environment variables sourced from a Kubernetes secret named `aoai-secret`.
   - `Dockerfile` is used to build a Docker image for the FastAPI application. Base image is from `mcr.microsoft.com/azureml/promptflow/promptflow-runtime:latest`. 
   - copies application code into the image
   - installs dependencies
   - FastAPI main.py describes three routes: `/yaml_basic_flow`, `/class_basic_flow`, and `function_basic_flow`
   - `run.sh` is bash script used to start FastAPI with OpenTelemetry Collector
   using uvicron server `uvicorn main:app --host --port`

   - **Step: Deploy OTel collector to AKS**The deployment to AKS includes setting up an OpenTelemetry collector and export telemtery traces to Application Insights in Azure Monitor, enhancing the observability of the deployed application.
   - installs OpenTelemtry instrumentation libraries