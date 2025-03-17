import json
import boto3
import base64

# Initialize AWS clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
MODEL_ID = "anthropic.claude-3-7-sonnet-20250219-v1:0"

def process_document(event, context):

    print("Event received:", json.dumps(event, indent=2))

    try:
            bucket_name = event['Records'][0]["s3"]["bucket"]["name"]
            object_key = event['Records'][0]["s3"]["object"]["key"]

            if not object_key.lower().endswith('.csv'):
                print(f"file not valid")
                return { 'statusCode': 403 , 'message': "file format is not valid"}
            
            image_data = s3.get_object(Bucket=bucket_name, Key= object_key)['Body'].read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # get the prompt 
            prompt = generate_prompt()

            response = invoke_claude_3_multimodal(prompt, base64_image)
        
            # Parse the JSON response
            print(f"New file uploaded: {object_key} in bucket {bucket_name}, base54 {len(base64_image)}, response prompt {response}")

    except Exception as ex: 
        print(f"Error general {ex}")

    return {
        "statusCode": "",
        "body":"process document"
    }



def generate_prompt():
    return """

        Analyze the provided cloud cost report and extract insights based on FinOps best practices. The analysis should cover the following areas:

        1️⃣ Cost Breakdown & Trends
            •	Daily and total cost trends for different applications.
            •	Identify the top applications contributing to the overall cost.
            •	Highlight any unexpected spikes or cost anomalies.

        2️⃣ Cost Optimization Opportunities
            •	Detect underutilized or idle resources that can be downsized or terminated.
            •	Identify cost inefficiencies such as over-provisioned instances.
            •	Provide right-sizing recommendations.

        3️⃣ Cost Leakages & Inefficiencies
            •	Highlight any sudden increases in spending.
            •	Identify areas where cost is accumulating but value delivery is unclear.
            •	Detect anomalous spending patterns that may require investigation.

        4️⃣ Recommendations for FinOps Teams
            •	Suggestions for budget allocation per application.
            •	Forecasting insights for better cost planning.
            •	Potential savings from reserved instances, spot instances, or autoscaling.

        Instructions:
            •	Extract the relevant insights as accurately as possible.
            •	If any anomalies are detected, provide an explanation of their potential causes.
            •	Present cost trends in an easy-to-understand format (graphs, tables, and summaries).
            •	Ensure all cost values are in currency format and include total calculations.
    

        Return the extracted data in the following JSON format:
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



def invoke_claude_3_multimodal(prompt, base64_image_data):
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "text",
                        "source": {
                            "type": "base64",
                            "media_type": "text/csv",
                            "data": base64_image_data,
                        },
                    },
                ],
            }
        ],
    }

    try:
        response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(request_body))
        return json.loads(response['body'].read())
    except bedrock.exceptions.ClientError as err:
        print(f"Bedrock ClientError: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
        raise
    except json.JSONDecodeError as err:
        print(f"Failed to parse Bedrock response: {str(err)}")
        raise