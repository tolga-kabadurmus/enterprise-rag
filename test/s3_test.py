import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="ENTERPRISERAGDEV",
    aws_secret_access_key="enterprise-rag-dev-password-change-me",
    # region_name="us-east-1",
)

print(s3.list_buckets())