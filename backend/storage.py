from __future__ import annotations

import json

import boto3
from botocore.config import Config as BotoCfg


def r2_client(endpoint: str, access_key: str, secret_key: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BotoCfg(s3={"addressing_style": "virtual"}, signature_version="s3v4"),
        region_name="auto",
    )


def get_audio_url(s3, bucket: str, item_id: str, ttl: int = 90) -> str:
    key = f"{item_id}.mp3"
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=ttl
    )


def get_transcript(s3, bucket: str, item_id: str) -> dict:
    key = f"{item_id}.json"
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read())
