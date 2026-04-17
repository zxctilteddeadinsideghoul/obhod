from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import urlparse
from uuid import uuid4

from minio import Minio

from app.core.config import Settings


class ObjectStorage:
    def __init__(self, settings: Settings) -> None:
        endpoint_url = urlparse(settings.minio_endpoint)
        endpoint = endpoint_url.netloc or endpoint_url.path
        secure = endpoint_url.scheme == "https"

        self.bucket = settings.minio_bucket
        self.client = Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )

    def upload(self, file_name: str, content_type: str, content: bytes) -> str:
        self._ensure_bucket()
        object_name = self._object_name(file_name)
        self.client.put_object(
            self.bucket,
            object_name,
            BytesIO(content),
            length=len(content),
            content_type=content_type,
        )
        return f"s3://{self.bucket}/{object_name}"

    def download(self, storage_uri: str) -> bytes:
        bucket, object_name = self._parse_storage_uri(storage_uri)
        response = self.client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def _ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def _object_name(self, file_name: str) -> str:
        today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        return f"attachments/{today}/{uuid4()}-{safe_name}"

    def _parse_storage_uri(self, storage_uri: str) -> tuple[str, str]:
        if not storage_uri.startswith("s3://"):
            raise ValueError("Unsupported storage URI")

        raw_path = storage_uri.removeprefix("s3://")
        bucket, _, object_name = raw_path.partition("/")
        if not bucket or not object_name:
            raise ValueError("Invalid storage URI")
        return bucket, object_name
