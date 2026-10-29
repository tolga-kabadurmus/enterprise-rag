import boto3

from diagnostic_settings import S3DiagnosticSettings

settings = S3DiagnosticSettings()

s3 = boto3.client(
    "s3",
    endpoint_url=str(settings.endpoint_url),
    aws_access_key_id=settings.access_key_id,
    aws_secret_access_key=settings.secret_access_key.get_secret_value(),
    region_name=settings.region,
)

print(s3.list_buckets())
