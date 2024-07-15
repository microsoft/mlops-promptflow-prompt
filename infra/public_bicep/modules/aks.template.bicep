metadata description = 'Creates an Azure Kubernetes Service (AKS) cluster.'
@description('The name for the AKS managed cluster')
param name string

@description('The name for the Azure container registry (ACR)')
param acrname string


// @description('The name of the keyvault to grant access')
// param keyVaultName string

@description('The Azure region/location for the AKS resources')
param location string = resourceGroup().location

@description('The name of the resource group for the managed resources of the AKS cluster')
param nodeResourceGroupName string = ''

@description('The managed cluster SKU.')
@allowed([ 'Free', 'Paid', 'Standard' ])
param sku string = 'Free'

@description('Id of the user or app to assign application roles')
param pId string = ''


// Create the primary AKS cluster resources and system node pool
module managedCluster './aks/aks.bicep' = {
  name: 'managed-cluster'
  params: {
    aks_cluster_name: name
    location: location
    nodeResourceGroupName: nodeResourceGroupName
    sku: sku
    containerRegistryName: acrname
    principalId: pId}  
}



// Module outputs
@description('The resource name of the AKS cluster')
output clusterName string = managedCluster.outputs.clusterName

@description('The AKS cluster identity')
output clusterIdentity object = managedCluster.outputs.clusterIdentity

