# MLOps for PromptFlow AI Studio Resource provisioning

## Steps
  ### az cli
  az login -t <tenantId>
  az account set --subscription <subscription_id>
  az deployment group create --resource-group <resourcegroup_name> --template-file ./infra/main.bicep

  ### azd 
  azd auth login
  azd config set defaults.subscription <subscriptionid>
  azd config set defaults.resourcegroup <resourcegroup> 
  azd init
  azd provision / up
