import io
import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')


TABLE_TRANSACCION = os.environ['TABLE_TRANSACCION']
TABLE_MEMORY_LAYER = os.environ['TABLE_MEMORY_LAYER']

def put_new_transaccion(transactionId, response_model):
    print(f"model response {response_model}")
    item = {
        "transactionId": transactionId ,
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
