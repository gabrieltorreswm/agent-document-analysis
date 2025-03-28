import json
import boto3
import os

ses_client = boto3.client("ses")  # use your region
s3 = boto3.client('s3')
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = os.environ['BUCKET_NAME']
TABLE_TRANSACCION = os.environ['TABLE_TRANSACCION']

def notify_summary(event, context):
    print(f"Event received: {event}")
    detail = event.get("detail", {})
    transactionId = detail.get("transactionId")
    # Example: get the detail
    print("🔍 detail:",detail.get("transactionId"))
    url_signed = get_url_s3(transactionId)
    mode_data_response = get_model_reponse_by_id(transactionId)
    sendMessageEmail(mode_data_response,url_signed)

    return { "statusCode":200 }




def sendMessageEmail(data,url_signed):
    print(f"url_signed: {url_signed} {data}")
    response_model = data.get("response_model")
    html_body = get_body_message(json.loads(response_model),url_signed)

    try:
        response = ses_client.send_email(
            Source="gtorresp@bolivariano.com",  # Must be a verified email in SES
            Destination={
                "ToAddresses": ["gtorresp@bolivariano.com"]  # Can also be a list
            },
            Message={
                "Subject": {"Data": "🚀 AWS FinOps Cost Report"},
                "Body": {
                    "Html": {"Data": html_body}
                }
            }
        )

        return response
    except Exception as ex:
        print(f"Error: {ex}")


def get_url_s3(transactionId):
    try:
        object_key = f"cost-chart-{transactionId}.png"
        s3 = boto3.client("s3")
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': object_key},
            ExpiresIn=3600  # 1 hour
        )

        return url

    except Exception as ex:
        print(f"Error {ex}")



def get_body_message(data_response_model,url_signed):

    try:
         # Custom email subject & message body
        print(f'data_response_model : {data_response_model}')

        total_cost = data_response_model["costSummary"]["totalCost"]
        top_apps = data_response_model["costSummary"]["costByApplicationsByDesc"]
        trend = data_response_model["costSummary"]["CostTrend"]
        underutilized_resources = data_response_model["optimizationOpportunities"]["underutilizedResources"]
        over_provisioned_resources = data_response_model["optimizationOpportunities"]["overProvisionedResources"]
        cost_anomalies = data_response_model["costAnomalies"]["unexpectedSpikes"]
        recommendations = data_response_model["recommendations"]["costSavingStrategies"]

        # Format top-cost applications
        top_apps_str = "\n".join(
            [f"- {app['application']}: {app['cost']}" for app in top_apps]
        )

        # Format daily cost trend
        trend_str = "\n".join(
            [f"* {app['month']}: {app['cost']}" for app in trend]
        )

        # Format underutilized resources
        underutilized_str = "\n".join([f"   - {item}" for item in underutilized_resources])

        # Format over-provisioned resources
        over_provisioned_str = "\n".join([f"   - {item}" for item in over_provisioned_resources])

        # Format cost anomalies
        anomalies_str = "\n".join(
            [f"* {anomaly}" for anomaly in cost_anomalies]
        )

        # Format recommendations
        recommendations_str = "\n".join([f"   - {rec}" for rec in recommendations])


        email_subject = "🚀 AWS FinOps Cost Report"

        email_body = f"""
            <html>
            <head>
                <style>
                body {{ font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #333; }}
                h2 {{ color: #2F855A; }}
                h3 {{ margin-bottom: 0; }}
                p {{ margin-top: 0; }}
                ul {{ margin-top: 0; }}
                .section-title {{ font-weight: bold; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <p>¡Hola! Espero todo este yendo muy bien. Aca les comparto el reporte de Cognito, generado y analizado por un agente IA cloud</p>
                <p>Queremos llevar nuestros análisis financieros en la nube al siguiente nivel. Nuestra meta es desarrollar un agente inteligente que rastree y explique los cambios en los costos de nuestras aplicaciones AWS.</p>
                
                <h3>📅 Costos Mensuales Mas Alto</h3>
                <pre>{trend_str}</pre>

                <img src="{url_signed}" alt="Chart" style="height: 400px; width: 700px">Cargando Imagen...</img>

                <h3>📌 Top Costos por Aplicación más alto</h3>
                <pre>{top_apps_str}</pre>

                <h3>🚨 Anomalías de costos</h3>
                <pre>{anomalies_str if cost_anomalies else "No anomalies detected."}</pre>

                <h3>💡 Recomendaciones para ahorrar costos</h3>
                <pre>{recommendations_str if recommendations else "No recommendations at this time."}</pre>

                <p style="margin-top: 30px;">
                Saludos,<br/>
                <strong>Servicios Cloud</strong>
                </p>
            </body>
            </html>
            """
        return email_body
    except Exception as ex:
        print(f"Error get_body_message {ex}")

        return None
    
        
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