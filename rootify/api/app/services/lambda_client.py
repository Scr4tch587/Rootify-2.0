import os
import json
import boto3
import anyio

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
LAMBDA_NAME = os.getenv("LAMBDA_ARTIFACT_WRITER_NAME")

_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    if not (AWS_REGION and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and LAMBDA_NAME):
        return None
    _client = boto3.client(
        "lambda",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    return _client

def _invoke_sync(payload: dict):
    client = _get_client()
    if client is None:
        return
    client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )

async def invoke_artifact_writer(payload: dict):
    try:
        await anyio.to_thread.run_sync(_invoke_sync, payload)
    except Exception:
        return
