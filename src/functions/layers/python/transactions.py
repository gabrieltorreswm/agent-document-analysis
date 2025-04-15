from boto3.dynamodb.conditions import Key
import json
import boto3
import os
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb')


TABLE_TRANSACCION = os.environ['TABLE_TRANSACCION']

def put_transaction(transactionId, response_model,report_type):
    print(f"model response {response_model}")
    item = {
        "transactionId": transactionId,
        "report_type": report_type,
        "createdAt": datetime.utcnow().isoformat(),
        "response_model": json.dumps(response_model)
    }
     
    try:
        table_transaction = dynamodb.Table(TABLE_TRANSACCION)
        response = table_transaction.put_item(Item=item)

        print(f"table transaccion respponse: ${response}")
        return response
        
    except Exception as ex:
        print(f"ex ${ex}")
