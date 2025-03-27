import json

def notify_summary(event, context):
    print("Event received:", json.dumps(event, indent=2))
    return { "statusCode":200 }