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
3. Enter the sercurity group id where you want to change the inbound rule.
4. Confirmations for creating roles and resources.
5. Option to save these parameters in a configuration file for future deployments.


-- destroy the created resources 

sam delete
```

## 