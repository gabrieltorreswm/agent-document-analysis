import json
import boto3
import io
import csv
import os
import uuid
from promps import generate_prompt
from urllib.parse import unquote

sns_client = boto3.client('sns')

# Initialize AWS clients
s3 = boto3.client('s3')

def process_document_daily(event, context):
    print("Event received:", json.dumps(event, indent=2))

    try:
        bucket_name = event['Records'][0]["s3"]["bucket"]["name"]
        object_key = event['Records'][0]["s3"]["object"]["key"]
        object_key_unquote = unquote(object_key)
        object_key__search = object_key_unquote.replace("+", " ")

        print(f"object_key {object_key} uncode_onjectKey {unquote(object_key)}")

        transactionId = str(uuid.uuid4())
        
        if not object_key.lower().endswith('.csv'):
            print(f"file not valid")
            return { 'statusCode': 403 , 'message': "file format is not valid"}
        
        image_data = s3.get_object(Bucket=bucket_name, Key= object_key__search)['Body'].read()
    except Exception as ex: 
        print(f"Error general {ex}")
        return {
            "statusCode": 500,
            "body": f"Error general {ex}"
        }