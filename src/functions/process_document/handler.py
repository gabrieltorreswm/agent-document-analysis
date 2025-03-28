import json
import boto3
import io
import csv
import os
import uuid
from datetime import datetime
from promps import generate_prompt

sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

# Initialize AWS clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
MODEL_ID = os.environ['MODEL_ID']
SNS_TOPIC_EMAIL = os.environ['SNS_TOPIC_EMAIL']
BUCKET_NAME = os.environ['BUCKET_NAME']
SNS_TOPIC_CHART_CREATOR = os.environ['SNS_TOPIC_CHART_CREATOR']
TABLE_TRANSACCION = os.environ['TABLE_TRANSACCION']

def process_document(event, context):

    print("Event received:", json.dumps(event, indent=2))

    try:
            bucket_name = event['Records'][0]["s3"]["bucket"]["name"]
            object_key = event['Records'][0]["s3"]["object"]["key"]

            transactionId = str(uuid.uuid4())

            if not object_key.lower().endswith('.csv'):
                print(f"file not valid")
                return { 'statusCode': 403 , 'message': "file format is not valid"}
            
            image_data = s3.get_object(Bucket=bucket_name, Key= object_key)['Body'].read()
        
            # get the prompt 
            prompt = generate_prompt()
            csv_content = convert_csv(image_data.decode('utf-8'))

            response = invoke_claude_3_multimodal(prompt, csv_content)

            print(f'response model raw: {response}')
            print(f"reponse text {json.loads(response['content'][0]['text'])}")

            response_model = json.loads(response['content'][0]['text']) 
            put_transaction_id = put_new_transaccion(transactionId, response_model)
            sent_topic_notification = sendMessageTopic(transactionId)

            # Parse the JSON response
            print(f"Message n bucket {sent_topic_notification}, transactionId {transactionId} , put_transaction_id {put_transaction_id}")

            return response

    except Exception as ex: 
        print(f"Error general {ex}")

    return {
        "statusCode": "",
        "body":"process document"
    }


def convert_csv(csv_file):
    csv_content = ""
    csv_reader = csv.reader(io.StringIO(csv_file))
    csv_content = [row for row in csv_reader]

    # for row in csv_content:
    #     csv_content += ", ".join() + "\n"

    print(f' return convert csv : {csv_content}')
    return csv_content

def sendMessageTopic(payload):
    # Publish to SNS topic
    print(f"payload {payload} and ar {SNS_TOPIC_CHART_CREATOR}")
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_CHART_CREATOR,
            Message=json.dumps({ "transactionId": payload }),
            Subject="Generate a chart"  # optional
        )

        print(f"Message sent! ID: {response}")

        return response
    except Exception as ex:
        print(f"Exception ${ex}")

def invoke_claude_3_multimodal(prompt, csv_table):
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
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
        return json.loads(response['body'].read())
    except bedrock.exceptions.ClientError as err:
        print(f"Bedrock ClientError: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
        raise
    except json.JSONDecodeError as err:
        print(f"Failed to parse Bedrock response: {str(err)}")
        raise


def put_new_transaccion(transactionId, response_model):
    print(f"model response {response_model}")
    item = {
        "transactionId": transactionId ,
        "createdAt":datetime.utcnow().isoformat(),
        "response_model": json.dumps(response_model)
    }
     
    try:
        table_transaction = dynamodb.Table(TABLE_TRANSACCION)
        response = table_transaction.put_item(Item=item)

        print(f"table transaccion respponse: ${response}")
        return response
        
    except Exception as ex:
        print(f"ex ${ex}")
        
