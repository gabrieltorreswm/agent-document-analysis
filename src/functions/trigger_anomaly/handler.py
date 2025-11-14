import json
import urllib3

http = urllib3.PoolManager()

def trigger_anomaly(event, context):
    print(f"Event received: {event}")

    url = "http://agentic-mpc-alb-688972174.us-east-1.elb.amazonaws.com/analyze-observability"
    payload = {
        "prompt": "analize, show me all the data possible on your analize, all hots_name"
    }

    try:
        response = http.request(
            "POST",
            url,
            body=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"Response status: {response.status}")
        print(f"Response body: {response.data.decode('utf-8')}")

        return {
            "statusCode": response.status,
            "body": response.data.decode("utf-8")
        }

    except Exception as ex:
        print(f"Error calling {url}: {ex}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(ex)}"
        }