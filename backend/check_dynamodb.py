"""
Check DynamoDB table schema
"""
import boto3

dynamodb = boto3.client('dynamodb', region_name='ap-south-1')

# Describe table
response = dynamodb.describe_table(TableName='rti-sessions-dev')

print("Table Schema:")
print(f"Table Name: {response['Table']['TableName']}")
print(f"Key Schema: {response['Table']['KeySchema']}")
print(f"Attribute Definitions: {response['Table']['AttributeDefinitions']}")
print(f"TTL: {response['Table'].get('TimeToLiveDescription', 'Not configured')}")
