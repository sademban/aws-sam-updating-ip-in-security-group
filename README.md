## setup your aws access key required permission 
- you can google it and setup the acces key first

## deploy
from your  root directory just run the following: 
```
sam build

sam deploy --guided

-- Follow the Prompts:
1. A stack name (e.g., RdsSecurityGroupUpdateStack).
2. AWS region where you want to deploy.
3. Enter the sercurity group id where you want to change the inbound rule. ***
4. Confirmations for creating roles and resources.
5. Option to save these parameters in a configuration file for future deployments.


-- destroy the created resources 

sam delete
```

## *** note
```
This setup is to update the ip in the security group for the developers on the aws resources . 
As the ip frequently changes while you work from diffrent location, therfore this
simple configuration will help your team to update the ip in the SG of any aws resources. 

It feels like its not a big deal to automate but if there is anyway i can imporve the simple 
utility automation please comment.

-- future plan

i am planning to integrate this with skype bot so while you work in a team this configuration 
will simply help you update the ip in SG of required resources just by sending the name and ip 
to the dedicated channel in skype
```

## USE CASE
```
- after the resources are provisiones you can just simply send post request using curl to api gateway and update the ip address in SG
eg:
 curl -X POST https://<api-gateway>/<stage>/<resource> \
-H "Content-Type: application/json" \
-d '{"name": "johndoe", "ip": "1.1.1.1"}' 
```
