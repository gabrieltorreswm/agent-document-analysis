import json
import boto3
import os

ses_client = boto3.client("ses") 

from get_body_message import template
from mc_dynamodb import dynamodb_getItem

def notify_summary_mcp(event, context):
    # Get the data from the event
    try:
        
        print(f"Event received: {event}")
        detail = event.get("detail", {})
        print(f" detail {detail}")
        
        item_data = dynamodb_getItem(detail.get("id"))
        sendMessageEmail(item_data)
        
        print(f"item_data : {item_data}")
        
        return { "statusCode" : 200 }
    except Exception as ex:
        print(f"Error: {ex}")
        return { "statusCode" :500 }



def sendMessageEmail(item_data):
    additional_attributes = json.loads(item_data.get("additional_attributes"))
    data_analisis = item_data.get("data")
    
    html_body = get_body_message(data_analisis)

    try:
        response = ses_client.send_email(
            Source="gabrieltorreswm@gmail.com",  # Must be a verified email in SES
            Destination={
                "ToAddresses": ["gtorresp@bolivariano.com"]  # Can also be a list
            },
            Message={
                "Subject": {"Data": f"🚀 Analisis de Observabilidad"},
                "Body": {
                    "Html": {"Data": html_body }
                }
            }
        )
        print(f'fendMessageEmail : {response}')
        return response
    except Exception as ex:
        print(f"Error: {ex}")