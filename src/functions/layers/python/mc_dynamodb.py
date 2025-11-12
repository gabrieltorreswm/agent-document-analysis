from boto3.dynamodb.conditions import Key
import boto3
import os
from typing import Dict, Any, List

#TABLE_MEMORY_LAYER = os.getenv("TABLE_MEMORY_LAYER", "arn:aws:dynamodb:us-east-1:471112847654:table/agentic-mpc-data-store")


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("arn:aws:dynamodb:us-east-1:471112847654:table/agentic-mpc-data-store")

def dynamodb_getItem(item_id:str)-> Dict[str, Any]:
    try:
        print(f"🔍 querying {table}")

        response = table.get_item(Key={"id": item_id})
        
        if "Item" not in response:
            return {
                "success": False,
                "message": f"Item with id '{item_id}' not found"
            }
        
        item = response["Item"]
        print(f"response item {item}")
        return {
            "success": True,
            "item": item
        }

    except Exception as ex:
        print(f"❌ Error querying mmcp  memory layer{ex}")
        return None