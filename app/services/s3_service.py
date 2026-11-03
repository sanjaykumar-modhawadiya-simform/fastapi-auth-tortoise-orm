import boto3
import os


def upload_pdf_to_s3(pdf_buffer, filename):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL")
    )
    bucket_name = os.getenv("S3_BUCKET_NAME", "my-local-bucket")
    aws_account_id = os.getenv("AWS_ACCOUNT_ID", "123456789012")

    # Ensure bucket exists for MinIO development
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except Exception:
        s3_client.create_bucket(Bucket=bucket_name)

    s3_client.upload_fileobj(
        pdf_buffer,
        bucket_name,
        filename,
        ExtraArgs={'ContentType': 'application/pdf'}
    )

    # Generate presigned URL valid for 1 hour
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': filename},
        ExpiresIn=3600
    )
    return url.replace("minio:9000", "localhost:9000")
