targetScope = 'subscription'

@description('The resource group into which your Azure resources should be deployed.')
param resourceGroupName string

@description('The location into which your Azure resources should be deployed.')
param location string

@description('Name of the storage resource.')
param storageAccount string

@description('The type of storage account that should be deployed.')
param sku string = 'Standard_LRS'

@description('The type of storage account that should be deployed.')
param kind string = 'StorageV2'

@description('The storage access tier at which the storage account should be deployed.')
param accessTier string = 'Hot'

@description('Name of the key vault resource.')
param keyVaultName string

@description('Name of the application insights resource.')
param appInsightsName string

@description('Name of the container registry resource.')
param containerRegistryName string

@description('Open AI resource name.')
param aiServiceName string

@description('Name for the AI resource and used to derive name of dependent resources.')
param aiHubName string = 'mlopspfaihub'

@description('Friendly name for your Azure AI resource')
param aiHubFriendlyName string = 'MLOps Prompflow template resources for AI Studio.'

@description('Description of your Azure AI resource dispayed in AI studio')
param aiHubDescription string = 'This is an example AI resource for use in Azure AI Studio.'

@description('Name for the AI Hub Project name.')
param aiHubProjectName string = 'mlopspfproject'

@description('Friendly name for your Azure AI Hub Project resource')
param aiHubProjectFriendlyName string = 'AI Project for experimentation and evaluation'

@description('Id of the user or app to assign application roles')
param principalId string 
param principalType string = 'ServicePrincipal'  //'User'

param nodeResourceGroupName string

var llmsconfig = loadYamlContent('./llms.yaml')
var llmDeployments = array(contains(llmsconfig, 'deployments') ? llmsconfig.deployments : [])

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: resourceGroupName
  location: location
}

// storage
module stg './modules/storage.template.bicep' = {
  name: storageAccount
  scope: resourceGroup(rg.name)
  params:{
    storageAccountName: storageAccount
    location: rg.location
    kind: kind
    accessTier: accessTier
    accountType: sku
  }
}

// key vault
module kv './modules/keyvault.template.bicep' = {
  name: keyVaultName
  scope: resourceGroup(rg.name)
  params: {
    keyVaultName: keyVaultName
    location: rg.location
  }
}

// application insights
module appInsightsResource './modules/appinsights.template.bicep' = {
  name:appInsightsName
  scope: resourceGroup(rg.name)
  params: {
    appInsightsName: appInsightsName
    location: rg.location
  }
}

// container registry
 module containerRegistryResource './modules/containerregistry.template.bicep' = {
  name: containerRegistryName
  scope: resourceGroup(rg.name)
  params: {
    containerRegistryName: containerRegistryName
    location: rg.location
  }
 }

 // OpenAI
  module ai './modules/aiservice.template.bicep' = {
  name: aiServiceName 
  scope: resourceGroup(rg.name)
  params: {
    aiServicesName: aiServiceName
    location: rg.location
    llm_deployments: llmDeployments
  }
 }

module aiHub './modules/ai-hub.bicep' = {
  name: 'aihubresource'
  scope: resourceGroup(rg.name)
  params: {
    // workspace organization
    aiHubName: aiHubName
    aiHubFriendlyName: aiHubFriendlyName
    aiHubDescription: aiHubDescription
    aiHubProjectName: aiHubProjectName
    aiHubProjectFriendlyName: aiHubProjectFriendlyName
    location: location

    // dependent resources
    aiServicesId: ai.outputs.aiservicesID
    aiServicesTarget: ai.outputs.aiservicesTarget
    applicationInsightsId: appInsightsResource.outputs.applicationInsightsId
    containerRegistryId: containerRegistryResource.outputs.containerRegistryId
    keyVaultId: kv.outputs.keyvaultId
    storageAccountId: stg.outputs.storageId
  }
}

// Assign roles to the specified principal

module userAcrRolePush './modules/role.bicep' = {
  name: 'user-acr-role-push'
  scope: rg
  params: {
    principalId: principalId
    roleDefinitionId: '8311e382-0749-4cb8-b61a-304f252e45ec'
    principalType: principalType
  }
}

module userAcrRolePull './modules/role.bicep' = {
  name: 'user-acr-role-pull'
  scope: rg
  params: {
    principalId: principalId
    roleDefinitionId: '7f951dda-4ed3-4680-a7ca-43fe172d538d'
    principalType: principalType
  }
}

module aks './modules/aks.template.bicep' = {
  name: 'aks'
  scope: rg
  params: {
    name: 'aks-cluster'
    location: location
    acrname: containerRegistryName
    pId: principalId
    nodeResourceGroupName: nodeResourceGroupName
  }
}


