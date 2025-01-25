import json
import logging

from minio import Minio

from config import get_settings

logger = logging.getLogger(__name__)


class MinioManager:

    def __init__(self):
        settings = get_settings()

        self.client = Minio(
            endpoint=f"{settings.MINIO_PROD_HOST}:{settings.MINIO_API_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
            cert_check=False,
        )

        buckets = [
            settings.MINIO_IMAGES_BUCKET,
            settings.MINIO_3D_FILES_BUCKET,
            settings.MINIO_DECA_EMOTIONS_BUCKET
        ]

        for bucket_name in buckets:
            bucket_exists = self.client.bucket_exists(bucket_name)
            if not bucket_exists:
                self.client.make_bucket(bucket_name)
                logger.info(f"Created bucket {bucket_name}")
            else:
                logger.info(f"Bucket {bucket_name} already exists")

            self.client.set_bucket_policy(
                bucket_name=bucket_name,
                policy=MinioManager.__get_public_read_policy()
            )

    @staticmethod
    def __get_public_read_policy() -> json:
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "s3:GetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Resource": "arn:aws:s3:::*"
                }
            ]
        }
        return json.dumps(policy)
