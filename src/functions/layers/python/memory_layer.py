from boto3.dynamodb.conditions import Key
import json
import boto3
import os
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb')
TABLE_MEMORY_LAYER = os.environ['TABLE_MEMORY_LAYER']

def put_memory(response_model,report_type):
    print(f"put memory {response_model}")

    current_month = datetime.utcnow().strftime("%Y-%m")
    uuid_report = str(uuid.uuid4())
    print(current_month)  # → "2025-03"
    item = {
        "PK": f"memory#services#cognito" ,
        "SK": f"{current_month}#{report_type}#{uuid_report}" ,
        "context": json.dumps(response_model),
        "createdAt": datetime.utcnow().isoformat(),
    }
     
    try:
        table_transaction = dynamodb.Table(TABLE_MEMORY_LAYER)
        response = table_transaction.put_item(Item=item)

        print(f"table memory: ${response}")
        return response
        
    except Exception as ex:
        print(f"ex ${ex}")

def get_memory(services, date_month, type_memory):
    try:
        print(f"🔍 Query memory for service: {services}, date_month {date_month} type_memory {type_memory}")

        table = dynamodb.Table(TABLE_MEMORY_LAYER)

        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"memory#services#{services}") & 
                                   Key("SK").begins_with(f"{date_month}#{type_memory}"),
            Limit=1,  # Optional: only get the first one
            ScanIndexForward=False  # Get latest first
        )

        items = response.get("Items", [])

        if items:
            print(f"✅ Found memory item: {items[0]}")
            return items[0]
        else:
            print("⚠️ No memory found for this service/month/type.")
            return None

    except Exception as ex:
        print(f"❌ Error querying memory: {ex}")
        return None


