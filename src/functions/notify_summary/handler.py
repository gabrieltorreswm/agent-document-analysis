import json
import boto3
import os

ses_client = boto3.client("ses")  # use your region
s3 = boto3.client('s3')


BUCKET_NAME = os.environ['BUCKET_NAME']

def notify_summary(event, context):
    print(f"Event received: {event}")
    detail = event.get("detail", {})
    transactionId = detail.get("transactionId")
    # Example: get the detail
    print("🔍 detail:",detail.get("transactionId"))
    url_signed = get_url_s3(transactionId)
    sendMessageEmail(url_signed)

    return { "statusCode":200 }




def sendMessageEmail(url_signed):
    print(f"url_signed: {url_signed}")
    html_body = f"""
            <html>
                <body>
                    <h2>Your chart is ready!</h2>
                    <img src="{url_signed}" alt="Chart" />
                </body>
                </html>
    """

    try:
        response = ses_client.send_email(
            Source="gtorresp@bolivariano.com",  # Must be a verified email in SES
            Destination={
                "ToAddresses": ["gtorresp@bolivariano.com"]  # Can also be a list
            },
            Message={
                "Subject": {"Data": "FindOps"},
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

        