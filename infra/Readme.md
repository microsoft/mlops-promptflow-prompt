# MLOps for PromptFlow AI Studio Resource provisioning

## Steps
  ### az cli
  az login -t <tenantId>
  az account set --subscription <subscription_id>
  az deployment group create --resource-group <resourcegroup_name> --template-file ./infra/main.bicep

  ### azd 
  azd auth login
  azd config set alpha.resourceGroupDeployments on
  azd config set defaults.subscription <subscriptionid>
  azd config set defaults.resourcegroup <resourcegroup> 
  azd init
    set new environment name
  azd provision / up

#### Sample output
  Provisioning Azure resources (azd provision)
  Provisioning Azure resources can take some time.


  WARNING: Feature 'resourceGroupDeployments' is in alpha stage.
  To learn more about alpha features and their support, visit https://aka.ms/azd-feature-stages.

  Subscription: <>
  Location: West US

  You can view detailed progress in the Azure Portal:
    link to the portal link

  (✓) Done: Cognitive Service: aisdemomtmb
  (✓) Done: Application Insights: appi-demo-mtmb
  (✓) Done: Key Vault: kv-demo-mtmb
  (✓) Done: Storage account: stdemomtmb
  (✓) Done: Container Registry: crdemomtmb
  (✓) Done: Search service: aisearchdemomtmb
  (✓) Done: Machine Learning Workspace: aih-demo-mtmb

SUCCESS: Your application was provisioned in Azure in 1 minute 4 seconds.
You can view the resources created under the resource group <> in Azure Portal:


## Create Project in AI Studio 
az login -t <tenantid>
az account set --subscription <subscriptionid>
az ml workspace create --kind project --hub-id <hub id from above deployment> --resource-group <resource group name> --name <project name>

confirm the project settings
az ml workspace show --name <project name> --resource-group <resourcegroup name>
