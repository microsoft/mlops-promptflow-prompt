@description('AI services name')
param aiServicesName string

@description('The location into which your Azure resources should be deployed.')
param location string

@description('The list of deployments for the AI service')
param llm_deployments array = []

@description('The kind of AI service')
param kind string = 'OpenAI'

resource open_ai 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: aiServicesName
  location: location
  kind: kind
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: toLower(aiServicesName)
  }
}

@batchSize(1)
resource llm_deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in llm_deployments: {
  parent: open_ai
  name: deployment.name
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
  }
  sku: contains(deployment, 'sku') ? deployment.sku : {
    name: 'Standard'
    capacity: 20
  }
}]

output aiservicesID string = open_ai.id
output aiservicesTarget string = 'https://${aiServicesName}.openai.azure.com/'
output endpoint string = open_ai.properties.endpoint
output endpoints object = open_ai.properties.endpoints
output name string = open_ai.name
