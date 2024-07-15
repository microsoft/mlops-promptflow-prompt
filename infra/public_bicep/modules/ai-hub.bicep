// Creates an Azure AI resource with proxied endpoints for the Azure AI services provider

@description('Azure region of the deployment')
param location string

@description('AI hub name')
param aiHubName string

@description('AI hub display name')
param aiHubFriendlyName string = aiHubName

@description('AI hub description')
param aiHubDescription string

@description('AI hub project name')
param aiHubProjectName string

@description('AI hub project display name')
param aiHubProjectFriendlyName string = aiHubName

@description('The SKU name to use for the AI Studio Hub Resource')
param skuName string = 'Basic'

@description('The SKU tier to use for the AI Studio Hub Resource')
@allowed(['Basic', 'Free', 'Premium', 'Standard'])
param skuTier string = 'Basic'

@description('Resource ID of the application insights resource for storing diagnostics logs')
param applicationInsightsId string

@description('Resource ID of the container registry resource for storing docker images')
param containerRegistryId string

@description('Resource ID of the key vault resource for storing connection strings')
param keyVaultId string

@description('Resource ID of the storage account resource for storing experimentation outputs')
param storageAccountId string

@description('Resource ID of the AI Services resource')
param aiServicesId string

@description('Resource ID of the AI Services endpoint')
param aiServicesTarget string

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-01-01-preview' = {
  name: aiHubName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: skuName
    tier: skuTier
  }

  properties: {
    // organization
    friendlyName: aiHubFriendlyName
    description: aiHubDescription

    // dependent resources
    keyVault: keyVaultId
    storageAccount: storageAccountId
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
  }
  kind: 'hub'

  resource aiServicesConnection 'connections@2024-01-01-preview' = {
    name: 'aoai'
    properties: {
      category: 'AzureOpenAI'
      target: aiServicesTarget
      authType: 'ApiKey'
      isSharedToAll: true
      credentials: {
        key: '${listKeys(aiServicesId, '2023-05-01').key1}'
      }
      metadata: {
        ApiType: 'Azure'
        ResourceId: aiServicesId
      }

    }
  }  
}

resource project 'Microsoft.MachineLearningServices/workspaces@2024-01-01-preview' = {
  name: aiHubProjectName
  location: location
  sku: {
    name: 'P3'
    tier: 'Basic'
  }
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: aiHubProjectFriendlyName
    hbiWorkspace: false
    v1LegacyMode: false
    publicNetworkAccess: 'Enabled'
    discoveryUrl: 'https://${location}.api.azureml.ms/discovery'
    // most properties are not allowed for a project workspace: "Project workspace shouldn't define ..."
    hubResourceId: aiHub.id
  }
}


output name string = aiHub.name
output id string = aiHub.id
output principalId string = aiHub.identity.principalId
