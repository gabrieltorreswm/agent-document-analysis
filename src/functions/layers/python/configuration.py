from boto3.dynamodb.conditions import Key
import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_MEMORY_LAYER = os.environ['TABLE_MEMORY_LAYER']


def get_configuretion():
    try:
        print(f"🔍 Query configuration")

        table = dynamodb.Table(TABLE_MEMORY_LAYER)

        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"configuration#report") & 
                                   Key("SK").begins_with(f"version#latest"),
            #FilterExpression=Attr("createdAt").gte("2025-04-01T00:00:00Z"),
            Limit=1,  # Optional: only get the first one
            ScanIndexForward=False  # Get latest first
        )

        items = response.get("Items", [])

        print(f"reponse configuration {items}")

        if items:
            print(f"✅ Found memory item: {items[0]}")
            return items[0]
        else:
            print("⚠️ No memory found for this service/month/type.")
            return None

    except Exception as ex:
        print(f"❌ Error querying memory: {ex}")
        return None