import requests
import json
import boto3
import io
import csv
import os
import uuid
from datetime import datetime

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

            response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
            data = response.json()

            print(f" data {data}")

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
            print(f"Message n bucket sent_topic_notification, transactionId {transactionId}")

            return response

    except Exception as ex: 
        print(f"Error general {ex}")

    return {
        "statusCode": "",
        "body":"process document"
    }



def generate_prompt():
    return """

        Analice el informe de costos de la nube proporcionado y extraiga información basada en las mejores prácticas de FinOps. El análisis debe abarcar las siguientes áreas:
        Antecedente: 
            - La tabla csv representa los costos de cognito pero dividida por cada aplicacion quien la consumio.
            - Cognito cobra basado en CognitoUserPoolsM2MTokenOp USD 0.00225 per client credential flow (M2M) token request in tier 1
            - Las aplicaciones son totalmente cloudnative, usan solo servicios de aws serverless como, cognito, dynamodb, stepfunction, s3 etc.


        1️⃣ Desglose y tendencias de costos
        • Tendencias de costos mensuales o diarios (dependiendo la table vcsv) para diferentes aplicaciones (maximo 10 registros).
        • Costos por toda las aplicaciones mensualmente, basate en el csv cargado previamente. (costByAppsPerMonths)
        • Identifique toda las aplicaciones que contribuyen al costo total.
        • Resalte cualquier aumento inesperado o anomalía en los costos.

        2️⃣ Oportunidades de optimización de costos
        • Detecte recursos y costos mas bajos, destacando que es la apliacion que es mas costo eficiente.
        • Proporcione recomendaciones basado en las buenas practicas para el servicio aws cognito.

        3️⃣ Fugas e ineficiencias de costos
        • Resalte cualquier aumento repentino y mejora en comparacion con los dias o meses anterios.
        • Detecte patrones de gasto anómalos que puedan requerir investigación. Por ejemplo realizar procesos de caches o reutilizacion de tokes de cognito.

        4️⃣ Recomendaciones para los equipos de FinOps
        • Sugerencias para la asignación de presupuesto por aplicación. 
        • Pronóstico de información para una mejor planificación de costos.

        Instrucciones:
        • Extraiga la información relevante con la mayor precisión posible.
        • Si detecta alguna anomalía, explique sus posibles causas.
        • Presente las tendencias de costos en un formato fácil de entender (gráficos, tablas y resúmenes).
        • Asegúrese de que todos los valores de costos estén en formato monetario e incluyan cálculos totales.

        Nota: la respuestas deben de ser en español.

        Devuelva los datos extraídos en el siguiente formato JSON unicamente, sin comentarios adicionales:
        {
            "costSummary": {
                "totalCost": "",
                "CostTrend": [
                    {"month":"","cost":"" }
                ],
                "costByApplicationsByDesc": [
                        {"application":"","cost":"" }
                ],
                 "costByAppsPerMonths": [
                        {"application": "", "month": "", "cost": ""}
                ]
            },
            "optimizationOpportunities": {
                "underutilizedResources": [],
                "overProvisionedResources": []
            },
            "costAnomalies": {
                "unexpectedSpikes": [],
                "highCostApplications": []
            },
            "recommendations": {
                "budgetAllocation": {},
                "forecastingInsights": [],
                "costSavingStrategies": []
            }
        }
    """

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
                        "text": prompt,
                    },
                     {  
                        "type":"text",
                        "text": f"aqui esta la table csv {csv_table}",
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
        


# def generate_chart():
#       # Generate Chart
#     applications = ["credimax", "onb/tarjeta", "cuenta/cliente", "venta-cruzada", "cliente", "cuenta/nomina"]
#     costs = [106.95, 54.03, 33.38, 6.00, 6.00, 6.39]

#     plt.figure(figsize=(8, 5))
#     plt.barh(applications, costs, color="blue", alpha=0.7)
#     plt.xlabel("Cost (USD)")
#     plt.title("Cloud Cost Breakdown")
#     plt.gca().invert_yaxis()

#     # Save to S3
#     s3 = boto3.client("s3")
#     img_data = io.BytesIO()
#     plt.savefig(img_data, format="png", dpi=300)
#     img_data.seek(0)

#     file_key = "cost-chart.png"
#     s3.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=img_data, ContentType="image/png")

#     return {"statusCode": 200, "body": f"Chart uploaded to S3://{BUCKET_NAME}/images/{file_key}"}
