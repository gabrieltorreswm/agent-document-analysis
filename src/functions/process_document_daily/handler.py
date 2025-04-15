import json
import boto3
import os
import uuid
from promps import generate_prompt
from datetime import datetime
from urllib.parse import unquote
from utils import convert_csv
from memory_layer import get_memory , put_memory
from transactions import put_transaction

sns_client = boto3.client('sns')

# Initialize AWS clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
MODEL_ID = os.environ['MODEL_ID']
SNS_TOPIC_EMAIL = os.environ['SNS_TOPIC_EMAIL']
BUCKET_NAME = os.environ['BUCKET_NAME']
SNS_TOPIC_CHART_CREATOR = os.environ['SNS_TOPIC_CHART_CREATOR']

def process_document_daily(event, context):
    print("Event received:", json.dumps(event, indent=2))

    try:
        bucket_name = event['Records'][0]["s3"]["bucket"]["name"]
        object_key = event['Records'][0]["s3"]["object"]["key"]
        object_key_unquote = unquote(object_key)
        object_key__search = object_key_unquote.replace("+", " ")

        print(f"object_key {object_key} uncode_onjectKey {unquote(object_key)}")

        transactionId = str(uuid.uuid4())
        
        if not object_key.lower().endswith('.csv'):
            print(f"file not valid")
            return { 'statusCode': 403 , 'message': "file format is not valid"}
        
        image_data = s3.get_object(Bucket=bucket_name, Key= object_key__search)['Body'].read()

        # get the prompt 
        prompt = generate_prompt()
        csv_content = convert_csv(image_data.decode('utf-8'))
        #current_month = datetime.utcnow().strftime("%Y-%m")
        #get_memory_response = get_memory("cognito",current_month,"daily")

        response = invoke_claude_3_multimodal(prompt, csv_content)

        print(f'response model raw: {response}')
        print(f"reponse text {json.dumps(response['content'][0]['text'],indent=4)}")

        response_model = json.loads(response['content'][0]['text']) 
        put_transaction_response = put_transaction(transactionId, response_model,"daily")
        #put_memory_response = put_memory(response_model,"month")
        sent_topic_notification = sendMessageTopic(transactionId,"daily")

        # Parse the JSON response
        print(f"Message n bucket {sent_topic_notification}, transactionId {transactionId} , put_transaction_id {put_transaction_response}")

        return {
            "statusCode": 200,
            "body": f"Message n bucket {sent_topic_notification}, transactionId {transactionId} , put_transaction_id {put_transaction_response}"
        }
    
    except Exception as ex: 
        print(f"Error general {ex}")
        raise Exception(f"The model not return the output expected") 
    

def invoke_claude_3_multimodal(prompt, csv_table):
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2400,
        "messages": [
            {
                "role": "user",
                "content": [
                    {  
                        "type":"text",
                        "text": f"Table csv {csv_table}",
                    },
                    {  
                        "type":"text",
                        "text": prompt,
                    }
                ],
            }
        ],
    }

    try:
        print(f"start invoka bedrock")
        response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(request_body))
        print(f"reponse model raw {response}")
        return json.loads(response['body'].read())
    except bedrock.exceptions.ClientError as err:
        print(f"Bedrock ClientError: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
        raise
    except json.JSONDecodeError as err:
        print(f"Failed to parse Bedrock response: {str(err)}")
        raise


def sendMessageTopic(payload, report_type):
    # Publish to SNS topic
    print(f"payload {payload} and ar {SNS_TOPIC_CHART_CREATOR}")
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_CHART_CREATOR,
            Message=json.dumps({ "transactionId": payload , "report_type": report_type, "bucket_name": BUCKET_NAME}),
            Subject="Generate a chart"  # optional
        )

        print(f"Message sent! ID: {response}")

        return response
    except Exception as ex:
        print(f"Exception {ex}")