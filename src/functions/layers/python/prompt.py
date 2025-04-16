from boto3.dynamodb.conditions import Key, Attr
import json
import boto3
import os
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb')
TABLE_MEMORY_LAYER = os.environ['TABLE_MEMORY_LAYER']


def get_prompt_daily():
    try:
        print(f"🔍 Rerport type:")

        table = dynamodb.Table(TABLE_MEMORY_LAYER)

        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"prompt#cognito#daily") & 
                                   Key("SK").begins_with(f"2025"),
            #FilterExpression=Attr("createdAt").gte("2025-04-01T00:00:00Z"),
            Limit=1,  # Optional: only get the first one
            ScanIndexForward=False  # Get latest first
        )

        items = response.get("Items", [])

        if items:
            print(f"✅ Found prompt item: {items[0]}")
            return items[0]
        else:
            print("⚠️ No prompt found for this ")
            return None

    except Exception as ex:
        print(f"❌ Error querying prompt: {ex}")
        return None
    
def get_prompt_month():
    try:
        print(f"🔍 Rerport type: ")

        table = dynamodb.Table(TABLE_MEMORY_LAYER)

        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"prompt#cognito#month") & 
                                   Key("SK").begins_with(f"2025"),
            #FilterExpression=Attr("createdAt").gte("2025-04-01T00:00:00Z"),
            Limit=1,  # Optional: only get the first one
            ScanIndexForward=False  # Get latest first
        )

        items = response.get("Items", [])

        if items:
            print(f"✅ Found prompt item: {items[0]}")
            return items[0]
        else:
            print("⚠️ No prompt found for this ")
            return None

    except Exception as ex:
        print(f"❌ Error querying prompt: {ex}")
        return None


