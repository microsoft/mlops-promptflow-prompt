@description('AI services name')
param aiServicesName string

@description('The location into which your Azure resources should be deployed.')
param location string

resource aiServices 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: aiServicesName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'AIServices' // or 'OpenAI' for OpenAI only
  properties: {
    apiProperties: {
      statisticsEnabled: false
    }
  }
}

output aiservicesID string = aiServices.id
output aiservicesTarget string = 'https://${aiServices.name}.openai.azure.com/'
