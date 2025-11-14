import json
import boto3
import os

ses_client = boto3.client("ses") 

#from body_message_mcp import get_template
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



def sendMessageEmail(item_data: dict):
    #additional_attributes = json.loads(item_data.get("additional_attributes"))
    print(f"sendmessageemail  {item_data}")
    
    raw_data = item_data.get("data")
    raw_additional = item_data.get("additional_attributes")


    print(f" raw_data {raw_data} and additional {raw_additional}")
    try:
        
        additional = {}
        if raw_additional:
            additional = json.loads(raw_additional)

        print(f"data additional {additional}")
        # Construye el HTML (puedes personalizarlo)

        html_body = f"""
            <h2>🚀 Análisis de Observabilidad 🤖</h2>
            <p><strong>Resumen:</strong> {raw_data}</p>
            <hr>
            <h3>Detalles adicionales</h3>
            <p>🤖 <strong>Razonamiento:</strong> {additional.get('reasoning', 'N/A')}</p>
            <p>📊 <strong>Impacto:</strong> {additional.get('impact', 'N/A')}</p>
            <p>🧾 <strong>Evidencia:</strong></p>
            {additional.get('evidence', 'N/A')}
            <p>⏱️ <strong>Latency:</strong> {additional.get('latency', 'N/A')}</p>
            <p>🔍 <strong>Causa raíz:</strong> {additional.get('root_cause', 'N/A')}</p>
            <p>📝 <strong>Análisis:</strong> {additional.get('analysis_summary', 'N/A')}</p>
        """


        response = ses_client.send_email(
            Source="gtorresp@bolivariano.com",  # Must be a verified email in SES
            Destination={
                "ToAddresses": ["gtorresp@bolivariano.com"]  # Can also be a list
            },
            Message={
                "Subject": {"Data": f"🚀 Análisis de Observabilidad "},
                "Body": {
                    "Html": {"Data": html_body }
                }
            }
        )
        print(f'fendMessageEmail : { response }')
        return response
    except Exception as ex:
        print(f"Error: {ex}")