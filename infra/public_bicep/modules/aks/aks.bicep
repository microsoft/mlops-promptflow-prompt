metadata description = 'Creates an Azure Kubernetes Service (AKS) cluster with a system agent pool.'

@description('The name of the AKS cluster.')
param aks_cluster_name string = 'aks-prompt-promptflow'

@description('The name of the resource group for the managed resources of the AKS cluster')
param nodeResourceGroupName string = ''

@description('The Azure region/location for the AKS resources')
param location string = resourceGroup().location

@description('The SKU tier for the AKS cluster')
@allowed(['Free', 'Paid', 'Standard'])
param sku string = 'Free'

@description('Configuration of AKS add-ons')
param addOns object = {}


resource aks_cluster 'Microsoft.ContainerService/managedClusters@2024-03-02-preview' = {
  name: aks_cluster_name
  location: location
  sku: {
    name: 'Base'
    tier: sku
  }
  kind: 'Base'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    kubernetesVersion: '1.28.9'
    dnsPrefix: '${aks_cluster_name}-dns'
    agentPoolProfiles: [
      {
        name: 'agentpool'
        count: 2
        vmSize: 'Standard_D4ds_v5'
        osDiskSizeGB: 128
        osDiskType: 'Ephemeral'
        kubeletDiskType: 'OS'
        maxPods: 110
        type: 'VirtualMachineScaleSets'
        maxCount: 5
        minCount: 2
        enableAutoScaling: true
        powerState: {
          code: 'Running'
        }
        orchestratorVersion: '1.28.9'
        enableNodePublicIP: false
        mode: 'System'
        osType: 'Linux'
        osSKU: 'Ubuntu'
        upgradeSettings: {
          maxSurge: '10%'
        }
        enableFIPS: false
        securityProfile: {
          sshAccess: 'LocalUser'
          enableVTPM: false
          enableSecureBoot: false
        }
      }
    ]

    addonProfiles: addOns
    nodeResourceGroup: !empty(nodeResourceGroupName) ? nodeResourceGroupName : 'rg-mc-${aks_cluster_name}'
    enableRBAC: true
    networkProfile: {
      networkPlugin: 'azure'
      networkPolicy: 'none'
      networkDataplane: 'azure'
      loadBalancerSku: 'Standard'
    }
    disableLocalAccounts: false
  }
}

resource agentpool 'Microsoft.ContainerService/managedClusters/agentPools@2024-03-02-preview' = {
  parent: aks_cluster
  name: 'agentpool'
  properties: {
    count: 2
    vmSize: 'Standard_D4ds_v5'
    osDiskSizeGB: 128
    osDiskType: 'Ephemeral'
    kubeletDiskType: 'OS'
    maxPods: 110
    type: 'VirtualMachineScaleSets'
    maxCount: 5
    minCount: 2
    enableAutoScaling: true
    enableNodePublicIP: false
    mode: 'System'
    osType: 'Linux'
    osSKU: 'Ubuntu'
    upgradeSettings: {
      maxSurge: '10%'
    }
    enableFIPS: false
    securityProfile: {
      sshAccess: 'LocalUser'
      enableVTPM: false
      enableSecureBoot: false
    }
  }
}


@description('The resource name of the AKS cluster')
output clusterName string = aks_cluster.name

@description('The AKS cluster identity')
output clusterIdentity object = {
  clientId: aks_cluster.properties.identityProfile.kubeletidentity.clientId
  objectId: aks_cluster.properties.identityProfile.kubeletidentity.objectId
  resourceId: aks_cluster.properties.identityProfile.kubeletidentity.resourceId
}
