using './main.bicep'

param resourceGroupName = readEnvironmentVariable('RESOURCE_GROUP_NAME', '')
param location = readEnvironmentVariable('LOCATION', '')
param storageAccount = readEnvironmentVariable('STORAGE_ACCT_NAME', '')
param aiHubName = readEnvironmentVariable('AIHUB_NAME', '')
param aiHubProjectName = readEnvironmentVariable('AIHUB_PROJECT_NAME', '')
param keyVaultName = readEnvironmentVariable('KEYVAULT_NAME', '')
param appInsightsName = readEnvironmentVariable('APPINSIGHTS_NAME', '')
param containerRegistryName = readEnvironmentVariable('CONTAINER_REGISTRY_NAME', '')
param aiServiceName = readEnvironmentVariable('AISERVICE_NAME', '')
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param principalType = readEnvironmentVariable('AZURE_PRINCIPAL_TYPE', 'User')
