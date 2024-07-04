param createMode string = 'default'

@description('name for the key vault')
param keyVaultName string

@description('The location into which your Azure resources should be deployed.')
param location string

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    createMode: createMode
    enabledForTemplateDeployment: true
    accessPolicies: []
  }
  tags: {
  }
}

output keyvaultId string = keyVault.id
