import json
import boto3
import os 
import re

ec2 = boto3.client('ec2')

SECURITY_GROUP_ID = os.environ['SECURITY_GROUP_ID'] # Replace with your actual Security Group ID

def lambda_handler(event, context):
    # Check if 'body' is present in the event
    if 'body' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('No body found in the event')
        }
    
    # Parse the body of the request
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format')
        }

    # Validate required parameters
    if 'name' not in body or 'ip' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required parameters: name and ip')
        }
    
    name = body['name']
    new_ip = body['ip'] + '/32'

    # Validate the IP format (basic IPv4 validation)
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', body['ip']):
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid IP format')
        }

    try:
        response = ec2.describe_security_groups(GroupIds=[SECURITY_GROUP_ID])
        security_group = response['SecurityGroups'][0]
        current_ip_permissions = security_group['IpPermissions']
        
        user_ip_entry = None
        ip_already_exists = False
        
        # First pass: Check if the IP already exists for a different user
        for permission in current_ip_permissions:
            for ip_range in permission.get('IpRanges', []):
                if ip_range['CidrIp'] == new_ip:
                    if 'Description' in ip_range:
                        if ip_range['Description'] == name:
                            # IP address is already correct for this user, no action needed
                            return {
                                'statusCode': 200,
                                'body': json.dumps(f"IP {new_ip} already exists for {name}. No changes made.")
                            }
                        else:
                            # The IP already exists for another user, don't update anything
                            ip_already_exists = True
                            break
        
        if ip_already_exists:
            return {
                'statusCode': 400,
                'body': json.dumps(f"IP {new_ip} is already associated with another user. No changes made.")
            }
        
        # Second pass: Find the current user's IP entry, if it exists
        for permission in current_ip_permissions:
            for ip_range in permission.get('IpRanges', []):
                if 'Description' in ip_range and ip_range['Description'] == name:
                    user_ip_entry = ip_range
        
        # If the user has an IP entry, update only if the IP differs
        if user_ip_entry:
            # No changes needed if the IP is the same
            if user_ip_entry['CidrIp'] == new_ip:
                return {
                    'statusCode': 200,
                    'body': json.dumps(f"IP {new_ip} already exists for {name}. No changes made.")
                }
            else:
                # Revoke the old IP address and add the new one
                ec2.revoke_security_group_ingress(
                    GroupId=SECURITY_GROUP_ID,
                    IpProtocol=permission['IpProtocol'],
                    FromPort=permission['FromPort'],
                    ToPort=permission['ToPort'],
                    CidrIp=user_ip_entry['CidrIp']
                )
                ec2.authorize_security_group_ingress(
                    GroupId=SECURITY_GROUP_ID,
                    IpPermissions=[
                        {
                            'IpProtocol': permission['IpProtocol'],
                            'FromPort': permission['FromPort'],
                            'ToPort': permission['ToPort'],
                            'IpRanges': [{'CidrIp': new_ip, 'Description': name}]
                        }
                    ]
                )
                return {
                    'statusCode': 200,
                    'body': json.dumps(f"IP updated for {name}")
                }
        
        # If the user's IP wasn't found, add the new IP
        ec2.authorize_security_group_ingress(
            GroupId=SECURITY_GROUP_ID,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',  # Adjust if you need to support other protocols
                    'FromPort': 3306,     # Adjust if you use different ports
                    'ToPort': 3306,
                    'IpRanges': [{'CidrIp': new_ip, 'Description': name}]
                }
            ]
        )
        return {
            'statusCode': 200,
            'body': json.dumps(f"New IP {new_ip} added for {name}")
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
