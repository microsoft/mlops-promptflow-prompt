param accountType string
param kind string = 'StorageV2'
param accessTier string = 'Hot'

@description('name for the storage account')
param storageAccountName string

@description('The location into which your Azure resources should be deployed.')
param location string

resource storage_resource 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: accountType
  }
  kind: kind
  properties: {
    accessTier: accessTier
    supportsHttpsTrafficOnly: true
  }
}

output storageId string = storage_resource.id
