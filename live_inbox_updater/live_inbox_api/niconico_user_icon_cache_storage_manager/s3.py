import boto3
import botocore.exceptions

from .base import LiveInboxApiNiconicoUserIconCacheStorageManager


class LiveInboxApiNiconicoUserIconCacheStorageS3Manager(
    LiveInboxApiNiconicoUserIconCacheStorageManager
):
    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str,
        region_name: str | None,
        access_key_id: str,
        secret_access_key: str,
    ):
        self.bucket_name = bucket_name

        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    def __create_niconico_user_icon_object_key(
        self,
        file_key: str,
        content_type: str,
    ) -> str:
        suffix: str | None = None
        if content_type == "image/jpeg":
            suffix = ".jpg"
        elif content_type == "image/png":
            suffix = ".png"
        elif content_type == "image/gif":
            suffix = ".gif"
        else:
            raise Exception(
                f"Unsupported content_type: {content_type}",
            )

        object_key = f"{file_key}{suffix}"
        return object_key

    def check_exists(
        self,
        file_key: str,
        content_type: str,
    ) -> bool:
        s3_client = self.s3_client
        bucket_name = self.bucket_name

        object_key = self.__create_niconico_user_icon_object_key(
            file_key=file_key,
            content_type=content_type,
        )

        try:
            s3_client.head_object(
                Bucket=bucket_name,
                Key=object_key,
            )
            return True
        except botocore.exceptions.ClientError as err:
            if err.response["Error"]["Code"] == "404":
                return False
            else:
                raise err

    def save(
        self,
        file_key: str,
        content_type: str,
        content: bytes,
    ) -> None:
        s3_client = self.s3_client
        bucket_name = self.bucket_name

        object_key = self.__create_niconico_user_icon_object_key(
            file_key=file_key,
            content_type=content_type,
        )

        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=content,
            ContentType=content_type,
        )
