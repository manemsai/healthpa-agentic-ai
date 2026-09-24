from __future__ import annotations

import boto3
import json


class BedrockLLM:
    def __init__(
        self,
        region: str = "us-east-1",
        model_id: str = "amazon.nova-lite-v1:0",
    ):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
        )

        self.model_id = model_id

    def generate(
        self,
        prompt: str,
        max_tokens: int = 700,
    ) -> str:

        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ],
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": 0,
                "topP": 0.9,
            },
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
        )

        result = json.loads(
            response["body"].read()
        )

        content = (
            result["output"]
            ["message"]
            ["content"]
        )

        text_parts = []

        for item in content:
            if "text" in item:
                text_parts.append(
                    item["text"]
                )

        return "\n".join(text_parts)