import json

def process_document(event, context):

    print("Event received:", json.dumps(event, indent=2))

    for record in event.get("Records", []):
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]
        
        print(f"New file uploaded: {object_key} in bucket {bucket_name}")

    return {
        "statusCode": "",
        "body":"process document"
    }