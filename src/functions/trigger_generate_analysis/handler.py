import json
import urllib3

http = urllib3.PoolManager()

def trigger_generate_analysis(event, context):
    print(f"Event received: {event}")

    url = "http://agentic-mpc-alb-688972174.us-east-1.elb.amazonaws.com/analyze-observability"
    payload = {
        "prompt": "analyze, make sure fecth all metrics define in the steps, save in dynamodb and send the event."
    }

    try:
        response = http.request(
            "POST",
            url,
            body=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=140
        )

        print(f"Response status: {response.status}")

        return {
            "statusCode": response.status,
            "body":"exitoso"
        }

    except Exception as ex:
        print(f"Error calling {url}: {ex}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(ex)}"
        }