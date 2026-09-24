import boto3
import json


REGION = "us-east-1"
MODEL_ID = "amazon.nova-lite-v1:0"


def main():
    client = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
    )

    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "What is 2 + 2? Return only the number."
                    }
                ],
            }
        ],
        "inferenceConfig": {
            "maxTokens": 50,
            "temperature": 0,
        },
    }

    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
    )

    result = json.loads(
        response["body"].read()
    )

    content = result["output"]["message"]["content"]

    for item in content:
        if "text" in item:
            print(item["text"])


if __name__ == "__main__":
    main()