import os
from pathlib import Path

from pydantic import BaseModel

from . import __VERSION__ as APP_VERSION
from .storage_type import StorageType, validate_storage_type_string


class AppConfig(BaseModel):
    live_inbox_hasura_url: str | None
    live_inbox_hasura_token: str | None

    niconico_user_icon_dir: Path | None

    storage_type: StorageType | None

    storage_file_dir: Path | None

    storage_s3_dir: str | None
    storage_s3_bucket_name: str | None
    storage_s3_endpoint_url: str | None
    storage_s3_region_name: str | None
    storage_s3_access_key_id: str | None
    storage_s3_secret_access_key: str | None

    useragent: str
    update_interval: int | None


def load_app_config_from_env() -> AppConfig:
    live_inbox_hasura_url = os.environ.get("LIVE_INBOX_HASURA_URL") or None
    live_inbox_hasura_token = os.environ.get("LIVE_INBOX_HASURA_TOKEN") or None

    niconico_user_icon_dir_string = os.environ.get("APP_NICONICO_USER_ICON_DIR") or None

    niconico_user_icon_dir: Path | None = None
    if niconico_user_icon_dir_string is not None:
        niconico_user_icon_dir = Path(niconico_user_icon_dir_string)

    storage_type_string = os.environ.get("APP_STORAGE_TYPE") or None
    storage_type: StorageType | None = None
    if storage_type_string is not None:
        if not validate_storage_type_string(storage_type_string):
            raise ValueError("Invalid storage type string. Use 'file' or 's3'.")

        storage_type = storage_type_string

    storage_file_dir: Path | None = None
    storage_file_dir_string = os.environ.get("APP_STORAGE_FILE_DIR") or None
    if storage_file_dir_string is not None:
        storage_file_dir = Path(storage_file_dir_string)

    storage_s3_dir = os.environ.get("APP_STORAGE_S3_DIR") or None
    storage_s3_bucket_name = os.environ.get("APP_STORAGE_S3_BUCKET_NAME") or None
    storage_s3_endpoint_url = os.environ.get("APP_STORAGE_S3_ENDPOINT_URL") or None
    storage_s3_region_name = os.environ.get("APP_STORAGE_S3_REGION_NAME") or None
    storage_s3_access_key_id = os.environ.get("APP_STORAGE_S3_ACCESS_KEY_ID") or None
    storage_s3_secret_access_key = (
        os.environ.get("APP_STORAGE_S3_SECRET_ACCESS_KEY") or None
    )

    useragent = os.environ.get("APP_USERAGENT") or None
    if useragent is None:
        useragent = f"LiveInboxBot/{APP_VERSION}"

    update_interval_string = os.environ.get("APP_UPDATE_INTERVAL") or None
    update_interval: int | None = None
    if update_interval_string is not None:
        update_interval = int(update_interval_string)

    return AppConfig(
        live_inbox_hasura_url=live_inbox_hasura_url,
        live_inbox_hasura_token=live_inbox_hasura_token,
        niconico_user_icon_dir=niconico_user_icon_dir,
        storage_type=storage_type,
        storage_file_dir=storage_file_dir,
        storage_s3_dir=storage_s3_dir,
        storage_s3_bucket_name=storage_s3_bucket_name,
        storage_s3_endpoint_url=storage_s3_endpoint_url,
        storage_s3_region_name=storage_s3_region_name,
        storage_s3_access_key_id=storage_s3_access_key_id,
        storage_s3_secret_access_key=storage_s3_secret_access_key,
        useragent=useragent,
        update_interval=update_interval,
    )
