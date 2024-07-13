metadata description = 'Creates an Azure Kubernetes Service (AKS) cluster.'
@description('The name for the AKS managed cluster')
param name string

@description('The name for the Azure container registry (ACR)')
param containerRegistryName string


@description('The name of the keyvault to grant access')
param keyVaultName string

@description('The Azure region/location for the AKS resources')
param location string = resourceGroup().location

@description('The name of the resource group for the managed resources of the AKS cluster')
param nodeResourceGroupName string = ''

@description('The managed cluster SKU.')
@allowed([ 'Free', 'Paid', 'Standard' ])
param sku string = 'Free'

@description('Id of the user or app to assign application roles')
param principalId string = ''


// Create the primary AKS cluster resources and system node pool
module managedCluster './aks/aks.bicep' = {
  name: 'managed-cluster'
  params: {
    aks_cluster_name: 'aks-cluster'
    location: location
    nodeResourceGroupName: nodeResourceGroupName
    sku: sku
    }
}


// Grant ACR Pull access from cluster managed identity to container registry
module containerRegistryAccess 'registry-access.bicep' = {
  name: 'cluster-container-registry-access'
  params: {
    containerRegistryName: containerRegistryName
    principalId: managedCluster.outputs.clusterIdentity.objectId
  }
}

// Give AKS cluster access to the specified principal
module clusterAccess './aks/aks-cluster-access.bicep' = {
  name: 'cluster-access'
  params: {
    clusterName: managedCluster.outputs.clusterName
    principalId: principalId
  }
}



// Module outputs
@description('The resource name of the AKS cluster')
output clusterName string = managedCluster.outputs.clusterName

@description('The AKS cluster identity')
output clusterIdentity object = managedCluster.outputs.clusterIdentity

