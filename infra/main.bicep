// Execute this main file to depoy Azure AI studio resources in the basic security configuraiton
targetScope = 'resourceGroup'

// Parameters
@minLength(2)
@maxLength(12)
@description('Name for the AI resource and used to derive name of dependent resources.')
param aiHubName string = 'mlopspfaihub'

@description('Friendly name for your Azure AI resource')
param aiHubFriendlyName string = 'MLOps Prompflow template resources for AI Studio.'

@description('Description of your Azure AI resource dispayed in AI studio')
param aiHubDescription string = 'This is an example AI resource for use in Azure AI Studio.'

@description('Name for the AI Hub Project name.')
param aiHubProjectName string = 'mlopspfproject'

@description('Friendly name for your Azure AI Hub Project resource')
param aiHubProjectFriendlyName string = 'Demo AI Project for experimentation and evaluation'

@description('Azure region used for the deployment of all resources.')
param location string = resourceGroup().location

@description('Azure OpenAI GPT Model Deployment Name')
param azureOpenAIModel string = 'gpt-35-turbo'

@description('Azure OpenAI GPT Model Name')
param azureOpenAIModelName string = 'gpt-35-turbo'

@description('Azure OpenAI GPT Model Version')
param azureOpenAIModelVersion string = '1106'

@description('Set of tags to apply to all resources.')
param tags object = {}

// Variables
var name = toLower('${aiHubName}')

// Create a short, unique suffix, that will be unique to each resource group
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)

var deployments = [
  {
    name: azureOpenAIModel
    model: {
      format: 'OpenAI'
      name: azureOpenAIModelName
      version: azureOpenAIModelVersion
    }
    sku: {
      name: 'Standard'
      capacity: 30
    }
  }
  {
    name: 'text-embedding-ada-002'
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    sku: {
      name: 'Standard'
      capacity: 30
    }
  }
]

// Dependent resources for the Azure Machine Learning workspace
module aiDependencies 'modules/dependent-resources.bicep' = {
  name: 'dependencies-${name}-${uniqueSuffix}-deployment'
  params: {
    location: location
    storageName: 'st${name}${uniqueSuffix}'
    keyvaultName: 'kv-${name}-${uniqueSuffix}'
    applicationInsightsName: 'appi-${name}-${uniqueSuffix}'
    containerRegistryName: 'cr${name}${uniqueSuffix}'
    aiServicesName: 'ais${name}${uniqueSuffix}'
    modeldeployments: deployments
    tags: tags
  }
}

module aiHub 'modules/ai-hub.bicep' = {
  name: 'ai-${name}-${uniqueSuffix}-deployment'
  params: {
    // workspace organization
    aiHubName: 'aih-${name}-${uniqueSuffix}'
    aiHubFriendlyName: aiHubFriendlyName
    aiHubDescription: aiHubDescription
    aiHubProjectName: aiHubProjectName
    aiHubProjectFriendlyName: aiHubProjectFriendlyName
    location: location
    tags: tags

    // dependent resources
    aiServicesId: aiDependencies.outputs.aiservicesID
    aiServicesTarget: aiDependencies.outputs.aiservicesTarget
    applicationInsightsId: aiDependencies.outputs.applicationInsightsId
    containerRegistryId: aiDependencies.outputs.containerRegistryId
    keyVaultId: aiDependencies.outputs.keyvaultId
    storageAccountId: aiDependencies.outputs.storageId
  }
}

output AOAI_BASE_ENDPOINT string = aiDependencies.outputs.aiservicesTarget
output APPINSIGHTS_CONNECTION_STRING string = aiDependencies.outputs.applicationInsightsConnectionString
output AOAI_API_KEY string = aiDependencies.outputs.aiservicesKey
output PROJECT_NAME string = aiHub.outputs.aiHubProjectName
output WORKSPACE_NAME string = aiHub.name

