@description('AI services name')
param aiServicesName string

@description('The location into which your Azure resources should be deployed.')
param location string

resource open_ai 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: aiServicesName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: toLower(aiServicesName)
  }
}

output aiservicesID string = aiServices.id
output aiservicesTarget string = 'https://${aiServicesName}.openai.azure.com/'
