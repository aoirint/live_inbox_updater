import time
import traceback
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta, timezone
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel
from schedule import Scheduler

from ..app_config import AppConfig
from ..live_inbox_api.niconico_live_program_manager import (
    LiveInboxApiNiconicoLiveProgramHasuraManager,
)
from ..live_inbox_api.niconico_user_icon_cache_metadata_manager import (
    LiveInboxApiNiconicoUserIconCacheMetadataHasuraManager,
)
from ..live_inbox_api.niconico_user_icon_cache_storage_manager import (
    LiveInboxApiNiconicoUserIconCacheStorageFileManager,
    LiveInboxApiNiconicoUserIconCacheStorageManager,
    LiveInboxApiNiconicoUserIconCacheStorageS3Manager,
)
from ..live_inbox_api.niconico_user_manager import NiconicoUserHasuraManager
from ..live_inbox_utility import update_job
from ..niconico_api.niconico_user_broadcast_history_client import (
    NiconicoApiNiconicoUserBroadcastHistoryNiconicoClient,
)
from ..niconico_api.niconico_user_icon_client import (
    NiconicoApiNiconicoUserIconNiconicoClient,
)
from ..storage_type import StorageType, validate_storage_type_string

logger = getLogger(__name__)


class SubcommandUpdateArgumentsStorageFileConfig(BaseModel):
    storage_file_dir: Path


class SubcommandUpdateArgumentsStorageS3Config(BaseModel):
    storage_s3_bucket_name: str
    storage_s3_endpoint_url: str
    storage_s3_region_name: str | None
    storage_s3_access_key_id: str
    storage_s3_secret_access_key: str


class SubcommandUpdateArguments(BaseModel):
    live_inbox_hasura_url: str
    live_inbox_hasura_token: str

    storage_type: StorageType
    storage_file_config: SubcommandUpdateArgumentsStorageFileConfig | None
    storage_s3_config: SubcommandUpdateArgumentsStorageS3Config | None

    useragent: str
    update_interval: int


def subcommand_update(args: SubcommandUpdateArguments) -> None:
    live_inbox_hasura_url = args.live_inbox_hasura_url
    live_inbox_hasura_token = args.live_inbox_hasura_token

    storage_type = args.storage_type
    storage_file_config = args.storage_file_config
    storage_s3_config = args.storage_s3_config

    useragent = args.useragent
    update_interval = args.update_interval

    niconico_user_manager = NiconicoUserHasuraManager(
        hasura_url=live_inbox_hasura_url,
        hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )

    niconico_user_icon_client = NiconicoApiNiconicoUserIconNiconicoClient(
        useragent=useragent,
    )

    niconico_user_icon_cache_metadata_manager = (
        LiveInboxApiNiconicoUserIconCacheMetadataHasuraManager(
            hasura_url=live_inbox_hasura_url,
            hasura_token=live_inbox_hasura_token,
            useragent=useragent,
        )
    )

    niconico_user_icon_cache_storage_manager: (
        LiveInboxApiNiconicoUserIconCacheStorageManager | None
    ) = None
    if storage_type == "file":
        if storage_file_config is None:
            raise Exception("Unexpected state.")

        niconico_user_icon_cache_storage_manager = (
            LiveInboxApiNiconicoUserIconCacheStorageFileManager(
                niconico_user_icon_dir=storage_file_config.storage_file_dir
                / "niconico_user_icons",
            )
        )
    elif storage_type == "s3":
        if storage_s3_config is None:
            raise Exception("Unexpected state.")

        niconico_user_icon_cache_storage_manager = (
            LiveInboxApiNiconicoUserIconCacheStorageS3Manager(
                dir="niconico_user_icons",
                bucket_name=storage_s3_config.storage_s3_bucket_name,
                endpoint_url=storage_s3_config.storage_s3_endpoint_url,
                region_name=storage_s3_config.storage_s3_region_name,
                access_key_id=storage_s3_config.storage_s3_access_key_id,
                secret_access_key=storage_s3_config.storage_s3_secret_access_key,
            )
        )
    else:
        raise Exception("Unexpected state.")

    niconico_user_broadcast_history_client = (
        NiconicoApiNiconicoUserBroadcastHistoryNiconicoClient(
            useragent=useragent,
        )
    )

    niconico_live_program_manager = LiveInboxApiNiconicoLiveProgramHasuraManager(
        hasura_url=live_inbox_hasura_url,
        hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )

    def _update_job() -> None:
        try:
            update_job(
                niconico_user_manager=niconico_user_manager,
                niconico_user_icon_client=niconico_user_icon_client,
                niconico_user_icon_cache_storage_manager=niconico_user_icon_cache_storage_manager,
                niconico_user_icon_cache_metadata_manager=niconico_user_icon_cache_metadata_manager,
                niconico_user_broadcast_history_client=niconico_user_broadcast_history_client,
                niconico_live_program_manager=niconico_live_program_manager,
            )
        except KeyboardInterrupt:
            raise
        except Exception:
            traceback.print_exc()

    scheduler = Scheduler()
    scheduler.every(update_interval).seconds.do(
        _update_job,
    )

    scheduler.run_all()

    scheduled_time: datetime | None = None
    while True:
        now = datetime.now(tz=timezone.utc)

        if scheduled_time is None or scheduled_time < now:
            scheduled_time_seconds = scheduler.idle_seconds
            if scheduled_time_seconds is not None:
                scheduled_time = now + timedelta(seconds=scheduled_time_seconds)
            else:
                scheduled_time = None
            logger.info(f"Next schedule: {scheduled_time}")

        scheduler.run_pending()
        time.sleep(1)


def execute_subcommand_update(
    args: Namespace,
) -> None:
    live_inbox_hasura_url: str = args.live_inbox_hasura_url
    live_inbox_hasura_token: str = args.live_inbox_hasura_token

    storage_type: StorageType | None = None
    storage_type_string: str = args.storage_type
    if not validate_storage_type_string(storage_type_string):
        raise ValueError("Invalid storage type string. Use 'file' or 's3'.")
    storage_type = storage_type_string

    storage_file_config: SubcommandUpdateArgumentsStorageFileConfig | None = None
    if storage_type == "file":
        storage_file_dir: Path | None = args.storage_file_dir
        if storage_file_dir is None:
            raise ValueError("Invalid storage file config.")

        storage_file_config = SubcommandUpdateArgumentsStorageFileConfig(
            storage_file_dir=storage_file_dir,
        )

    storage_s3_config: SubcommandUpdateArgumentsStorageS3Config | None = None
    if storage_type == "s3":
        storage_s3_bucket_name: str | None = args.storage_s3_bucket_name
        storage_s3_endpoint_url: str | None = args.storage_s3_endpoint_url
        storage_s3_region_name: str | None = args.storage_s3_region_name
        storage_s3_access_key_id: str | None = args.storage_s3_access_key_id
        storage_s3_secret_access_key: str | None = args.storage_s3_secret_access_key

        if (
            storage_s3_bucket_name is None
            or storage_s3_endpoint_url is None
            or storage_s3_access_key_id is None
            or storage_s3_secret_access_key is None
        ):
            raise ValueError("Invalid storage s3 config.")

        storage_s3_config = SubcommandUpdateArgumentsStorageS3Config(
            storage_s3_bucket_name=storage_s3_bucket_name,
            storage_s3_endpoint_url=storage_s3_endpoint_url,
            storage_s3_region_name=storage_s3_region_name,
            storage_s3_access_key_id=storage_s3_access_key_id,
            storage_s3_secret_access_key=storage_s3_secret_access_key,
        )

    useragent: str = args.useragent
    update_interval: int = args.update_interval

    subcommand_update(
        args=SubcommandUpdateArguments(
            live_inbox_hasura_url=live_inbox_hasura_url,
            live_inbox_hasura_token=live_inbox_hasura_token,
            storage_type=storage_type,
            storage_file_config=storage_file_config,
            storage_s3_config=storage_s3_config,
            useragent=useragent,
            update_interval=update_interval,
        ),
    )


def add_arguments_subcommand_update(
    parser: ArgumentParser,
    app_config: AppConfig,
) -> None:
    parser.add_argument(
        "--live_inbox_hasura_url",
        type=str,
        default=app_config.live_inbox_hasura_url,
        required=app_config.live_inbox_hasura_url is None,
    )
    parser.add_argument(
        "--live_inbox_hasura_token",
        type=str,
        default=app_config.live_inbox_hasura_token,
        required=app_config.live_inbox_hasura_token is None,
    )

    parser.add_argument(
        "--storage_type",
        type=str,
        default=app_config.storage_type,
        required=app_config.storage_type is None,
    )

    parser.add_argument(
        "--storage_file_dir",
        type=Path,
        default=app_config.storage_file_dir,
    )

    parser.add_argument(
        "--storage_s3_bucket_name",
        type=str,
        default=app_config.storage_s3_bucket_name,
    )
    parser.add_argument(
        "--storage_s3_endpoint_url",
        type=str,
        default=app_config.storage_s3_endpoint_url,
    )
    parser.add_argument(
        "--storage_s3_region_name",
        type=str,
        default=app_config.storage_s3_region_name,
    )
    parser.add_argument(
        "--storage_s3_access_key_id",
        type=str,
        default=app_config.storage_s3_access_key_id,
    )
    parser.add_argument(
        "--storage_s3_secret_access_key",
        type=str,
        default=app_config.storage_s3_secret_access_key,
    )

    parser.add_argument(
        "--useragent",
        type=str,
        default=app_config.useragent,
        required=app_config.useragent is None,
    )
    parser.add_argument(
        "--update_interval",
        type=int,
        default=app_config.update_interval,
        required=app_config.update_interval is None,
        help="Update interval in seconds",
    )

    parser.set_defaults(handler=execute_subcommand_update)
