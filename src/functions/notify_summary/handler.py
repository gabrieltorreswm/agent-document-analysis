import json
import boto3
import os

ses_client = boto3.client("ses")  # use your region
s3 = boto3.client('s3')
dynamodb = boto3.resource("dynamodb")
from get_body_message_daily import get_body_message_daily
from get_body_message_month import get_body_message_month
from configuration import get_configuretion

TABLE_TRANSACCION = os.environ['TABLE_TRANSACCION']

def notify_summary(event, context):
    
    try:
        # Get the data from the event
        print(f"Event received: {event}")
        detail = event.get("detail", {})
        transactionId = detail.get("transactionId")
        bucket_name = detail.get("bucket_name")
        report_type = detail.get("report_type")

        # Example: get the detail
        print(f"🔍 detail: {transactionId} {bucket_name} {report_type}")

        # Get the data from the dynamodb
        url_signed = get_url_s3(transactionId,bucket_name)
        mode_data_response = get_model_reponse_by_id(transactionId)

        # Send the email
        configuration = get_configuretion()

        if configuration.get("production"):
            sendMessageEmail(mode_data_response,url_signed,report_type)
        if configuration.get("development"):
            sendMessageEmail(mode_data_response,url_signed,report_type)

        return { "statusCode":200 }
    except Exception as ex:
        print(f"Error: {ex}")
        return { "statusCode" :500 }




def sendMessageEmail(data,url_signed,report_type):
    print(f"url_signed: {url_signed} {data}")
    response_model = data.get("response_model")
    if report_type == "daily":
        html_body = get_body_message_daily(json.loads(response_model),url_signed)
    else:
        html_body = get_body_message_month(json.loads(response_model),url_signed)

    try:
        response = ses_client.send_email(
            Source="gtorresp@bolivariano.com",  # Must be a verified email in SES
            Destination={
                "ToAddresses": ["gtorresp@bolivariano.com"]  # Can also be a list
            },
            Message={
                "Subject": {"Data": f"🚀 AWS FinOps Rerporte de Costos {'Diario' if report_type == 'daily' else 'Mensual'}"},
                "Body": {
                    "Html": {"Data": html_body}
                }
            }
        )
        print(f'fendMessageEmail : {response}')
        return response
    except Exception as ex:
        print(f"Error: {ex}")


def get_url_s3(transactionId,bucket_name):
    try:
        object_key = f"cost-chart-{transactionId}.png"
        s3 = boto3.client("s3")
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=51840  # 1 hour
        )

        return url

    except Exception as ex:
        print(f"Error {ex}")

    
        
def get_model_reponse_by_id(transaction_id):
    try:
        print(f" request transaction_id: {transaction_id}")
        table_transaction = dynamodb.Table(TABLE_TRANSACCION)
        response = table_transaction.get_item(
            Key={
                "transactionId": transaction_id
            }
        )
        print(f" resonse query: {response}")
        item = response.get("Item")
        if item:
            print(f"✅ Found transaction: {item}")
            return item
        else:
            print("⚠️ No item found with that transactionId.")
            return None

    except Exception as ex:
        print(f"Error getting item: {ex}")
        return None