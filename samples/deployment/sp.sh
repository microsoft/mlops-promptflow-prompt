spname="teamsdeployer"
roleName="Owner"
subscriptionId="691b572d-8686-481a-9757-4befaa7f9526"
servicePrincipalName="Azure-ARM-${spname}"

# Verify the ID of the active subscription
echo "Using subscription ID $subscriptionID"
echo "Creating SP for RBAC with name $servicePrincipalName, with role $roleName and in scopes     /subscriptions/$subscriptionId"

az ad sp create-for-rbac --name $servicePrincipalName --role $roleName --scopes /subscriptions/$subscriptionId --sdk-auth

echo "Please ensure that the information created here is properly save for future use."
