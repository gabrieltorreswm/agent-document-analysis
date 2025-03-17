import json
import boto3
import base64
import io
import csv
import os

sns_client = boto3.client('sns')

# Initialize AWS clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
MODEL_ID = os.environ['MODEL_ID']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
BUCKET_ARN = os.environ['BUCKET_ARN']

def process_document(event, context):

    print("Event received:", json.dumps(event, indent=2))

    try:
            bucket_name = event['Records'][0]["s3"]["bucket"]["name"]
            object_key = event['Records'][0]["s3"]["object"]["key"]

            if not object_key.lower().endswith('.csv'):
                print(f"file not valid")
                return { 'statusCode': 403 , 'message': "file format is not valid"}
            
            url_bucket = f's3://{bucket_name}/{object_key}'
            image_data = s3.get_object(Bucket=bucket_name, Key= object_key)['Body'].read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # get the prompt 
            prompt = generate_prompt()
            csv_content = convert_csv(image_data.decode('utf-8'))

            response = invoke_claude_3_multimodal(prompt, csv_content)

            # Parse the JSON response
            print(f"New file uploaded: {object_key} in bucket {bucket_name}, csv_content {csv_content}")

            print(f'response model raw: {response}')
            print(f"reponse text {json.loads(response['content'][0]['text'])}")

            print(f"model text {response['content'][0]['text']}")

            sent_notification = send_email(json.loads(response['content'][0]['text']))

            print(f"EndProcesss {sent_notification}")
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
        • Tendencias de costos diarios y totales para diferentes aplicaciones (solo 10 registros).
        • Identifique las principales aplicaciones que contribuyen al costo total.
        • Resalte cualquier aumento inesperado o anomalía en los costos.

        2️⃣ Oportunidades de optimización de costos
        • Detecte recursos infrautilizados o inactivos que puedan reducirse o cancelarse.
        • Identifique ineficiencias de costos, como instancias con exceso de aprovisionamiento.
        • Proporcione recomendaciones para el dimensionamiento adecuado.

        3️⃣ Fugas e ineficiencias de costos
        • Resalte cualquier aumento repentino en el gasto.
        • Identifique áreas donde los costos se acumulan, pero la entrega de valor no es clara.
        • Detecte patrones de gasto anómalos que puedan requerir investigación.

        4️⃣ Recomendaciones para los equipos de FinOps
        • Sugerencias para la asignación de presupuesto por aplicación. • Pronóstico de información para una mejor planificación de costos.
        • Ahorros potenciales gracias a instancias reservadas, instancias puntuales o escalado automático.

        Instrucciones:
        • Extraiga la información relevante con la mayor precisión posible.
        • Si detecta alguna anomalía, explique sus posibles causas.
        • Presente las tendencias de costos en un formato fácil de entender (gráficos, tablas y resúmenes).
        • Asegúrese de que todos los valores de costos estén en formato monetario e incluyan cálculos totales.

        Nota: la respuestas deben de ser en español 

        Devuelva los datos extraídos en el siguiente formato JSON:
        {
            "costSummary": {
                "totalCost": "",
                "dailyCostTrend": {},
                "topCostApplications": []
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


def send_email(data_response_model):
        # Custom email subject & message body
        print(f'data_response_model : {data_response_model}')

        total_cost = data_response_model["costSummary"]["totalCost"]
        top_apps = data_response_model["costSummary"]["topCostApplications"]
        daily_trend = data_response_model["costSummary"]["dailyCostTrend"]
        underutilized_resources = data_response_model["optimizationOpportunities"]["underutilizedResources"]
        over_provisioned_resources = data_response_model["optimizationOpportunities"]["overProvisionedResources"]
        cost_anomalies = data_response_model["costAnomalies"]["unexpectedSpikes"]
        recommendations = data_response_model["recommendations"]["costSavingStrategies"]

         # Format top-cost applications
        top_apps_str = "\n".join(
            [f"   - {app['name']}: {app['cost']}    " for app in top_apps]
        )

        # Format daily cost trend
        daily_trend_str = "\n".join(
            [f"   - {date}: {cost}     " for date, cost in daily_trend.items()]
        )

        # Format underutilized resources
        underutilized_str = "\n".join([f"   - {item}" for item in underutilized_resources])

        # Format over-provisioned resources
        over_provisioned_str = "\n".join([f"   - {item}" for item in over_provisioned_resources])

        # Format cost anomalies
        anomalies_str = "\n".join(
            [f"   - {anomaly['date']} | {anomaly['application']}: {anomaly['cost']}" for anomaly in cost_anomalies]
        )

        # Format recommendations
        recommendations_str = "\n".join([f"   - {rec}" for rec in recommendations])


        email_subject = "🚀 AWS FinOps Cost Report"
        email_body = f"""
        Hola a todos, espero todo este yendo muy bien.

        Envio el último reporte de costos:

        📊 **Total Costos:** {total_cost}

        **Top costos por Aplicación:**
        {top_apps_str}

        📅 **Costos Diarios:**
        {daily_trend_str}

        ⚠️ **Recursos subutilizados:**
        {underutilized_str if underutilized_resources else "No underutilized resources detected."}

        ⚙️ **Recursos sobreaprovisionados::**
        {over_provisioned_str if over_provisioned_resources else "No over-provisioned resources detected."}

        🚨 **Anomalías de costos (picos inesperados)::**
        {anomalies_str if cost_anomalies else "No anomalies detected."}

        💡 **Recomendaciones para ahorrar costos::**
        {recommendations_str if recommendations else "No recommendations at this time."}

        Saludos,  
        Servicios Cloud
        """

        # Publish message to SNS
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=email_body,  # Email body
            Subject=email_subject  # Email subject
        )

        return response