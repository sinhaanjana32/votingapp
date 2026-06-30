setup-script



az vmss run-command invoke --resource-group acdnd-c4-project --name udacity-vmss --instance-id 0 --command-id RunShellScript --scripts 'cd /home/udacityadmin/votingapp/azure-vote && export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=11630375-f7e5-41fd-a228-6fc1498d04ca;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/;LiveEndpoint=https://westus.livediagnostics.monitor.azure.com/;ApplicationId=0ea2b8b4-e5ca-42a7-b6cd-1791831c09e8" && python3 main.py'



az vmss run-command invoke --resource-group acdnd-c4-project --name udacity-vmss --instance-id 0 --command-id RunShellScript --scripts 'cd /home/udacityadmin/votingapp/azure-vote && export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=123b7294-765f-46ba-837d-1a1a206c2407;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/;LiveEndpoint=https://westus.livediagnostics.monitor.azure.com/;ApplicationId=fa2789b7-47e5-4913-a86f-a793acf5c0b1" && python3 main.py' && nohup python3 main.py >/tmp/votingapp.log 2>&1 & sleep 5 && ps -ef | grep main.py && cat /tmp/votingapp.log'


az vmss run-command invoke --resource-group acdnd-c4-project --name udacity-vmss --instance-id 0 --command-id RunShellScript --scripts 'cd /home/udacityadmin/votingapp/azure-vote && export APPLICATIONINSIGHTS_CONNECTION_STRING="<YOUR_CONNECTION_STRING>" && nohup python3 main.py >/tmp/votingapp.log 2>&1 & sleep 5 && ps -ef | grep main.py && cat /tmp/votingapp.log'


git add .
git commit -m "Disable Flask debug mode"
git push origin Deploy_to_VMSS

az vmss run-command invoke \
  --resource-group acdnd-c4-project \
  --name udacity-vmss \
  --instance-id 0 \
  --command-id RunShellScript \
  --scripts '
cd /home/udacityadmin/votingapp
git pull origin Deploy_to_VMSS
'



az monitor app-insights component create \
  --app votingapp-insights \
  --location westus \
  --resource-group acdnd-c4-project \
  --application-type web

  az monitor app-insights component show \
  --app votingapp-insights \
  --resource-group acdnd-c4-project \
  --query connectionString \
  --output tsv