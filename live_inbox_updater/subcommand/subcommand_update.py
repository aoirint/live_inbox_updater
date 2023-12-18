import hashlib
import time
import uuid
from argparse import ArgumentParser, Namespace
from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

from ..app_config import AppConfig
from ..live_inbox_api.niconico_live_program_manager import (
    LiveInboxApiNiconicoLiveProgramHasuraManager,
    LiveInboxApiNiconicoLiveProgramManager,
    LiveInboxApiNiconicoLiveProgramUpsertObject,
)
from ..live_inbox_api.niconico_user_icon_cache_metadata_manager import (
    LiveInboxApiNiconicoUserIconCacheMetadataHasuraManager,
    LiveInboxApiNiconicoUserIconCacheMetadataManager,
)
from ..live_inbox_api.niconico_user_icon_cache_storage_manager import (
    LiveInboxApiNiconicoUserIconCacheStorageFileManager,
    LiveInboxApiNiconicoUserIconCacheStorageManager,
)
from ..live_inbox_api.niconico_user_manager import (
    LiveInboxApiNiconicoUserManager,
    NiconicoUserHasuraManager,
)
from ..niconico_api.niconico_user_broadcast_history_client import (
    NiconicoApiNiconicoUserBroadcastHistoryClient,
    NiconicoApiNiconicoUserBroadcastHistoryNiconicoClient,
)
from ..niconico_api.niconico_user_icon_client import (
    NiconicoApiNiconicoUserIconClient,
    NiconicoApiNiconicoUserIconNiconicoClient,
)

logger = getLogger(__name__)


def fetch_uncached_niconico_user_icons(
    niconico_user_manager: LiveInboxApiNiconicoUserManager,
    niconico_user_icon_client: NiconicoApiNiconicoUserIconClient,
    niconico_user_icon_cache_metadata_manager: LiveInboxApiNiconicoUserIconCacheMetadataManager,
    niconico_user_icon_cache_storage_manager: LiveInboxApiNiconicoUserIconCacheStorageManager,
) -> None:
    """
    未取得のユーザアイコンを取得する
    """

    # ユーザアイコンURLリストを取得
    niconico_users = niconico_user_manager.get_all()
    enabled_niconico_users = list(
        filter(lambda niconico_user: niconico_user.enabled, niconico_users),
    )

    icon_urls: set[str] = set()
    for niconico_user in enabled_niconico_users:
        if niconico_user.icon_url is None:
            continue

        icon_urls.add(niconico_user.icon_url)

    # 取得済みのユーザアイコンURLリストを取得
    icon_cache_metadatas = niconico_user_icon_cache_metadata_manager.get_by_urls(
        urls=icon_urls,
    )
    cached_icon_urls: set[str] = set()
    for icon_cache_metadata in icon_cache_metadatas:
        cached_icon_urls.add(icon_cache_metadata.url)

    # TODO: 取得済みのユーザアイコンが消滅していないか確認

    # 未取得のユーザアイコンURLリストを作成
    uncached_icon_urls = icon_urls - cached_icon_urls
    logger.info(f"Found {len(uncached_icon_urls)} uncached niconico user icons")

    for icon_url in uncached_icon_urls:
        file_key = str(uuid.uuid4())
        fetched_at = datetime.now(tz=timezone.utc)

        # ユーザアイコンを取得
        niconico_user_icon = niconico_user_icon_client.get(url=icon_url)

        # ユーザアイコンを保存
        niconico_user_icon_cache_storage_manager.save(
            file_key=file_key,
            content_type=niconico_user_icon.content_type,
            content=niconico_user_icon.content,
        )

        file_size = len(niconico_user_icon.content)
        hash_md5 = hashlib.md5(niconico_user_icon.content).hexdigest()

        # ユーザアイコンのメタデータを保存
        niconico_user_icon_cache_metadata_manager.save(
            url=icon_url,
            fetched_at=fetched_at,
            file_size=file_size,
            hash_md5=hash_md5,
            content_type=niconico_user_icon.content_type,
            file_key=file_key,
        )

        time.sleep(1)

    logger.info(f"Fetched {len(uncached_icon_urls)} niconico user icons")


def update_niconico_live_programs(
    niconico_user_manager: LiveInboxApiNiconicoUserManager,
    niconico_user_broadcast_history_client: NiconicoApiNiconicoUserBroadcastHistoryClient,
    niconico_live_program_manager: LiveInboxApiNiconicoLiveProgramManager,
) -> None:
    niconico_users = niconico_user_manager.get_all()
    enabled_niconico_users = list(
        filter(lambda niconico_user: niconico_user.enabled, niconico_users),
    )

    logger.info(f"Found {len(enabled_niconico_users)} enabled niconico_users")
    for niconico_user in enabled_niconico_users:
        logger.info(
            f"niconico_user[remote_niconico_user_id={niconico_user.remote_niconico_user_id}]: "
            "Updating live programs"
        )

        fetch_time = datetime.now(tz=timezone.utc)
        user_broadcast_programs = niconico_user_broadcast_history_client.get_programs(
            niconico_user_id=niconico_user.remote_niconico_user_id,
            offset=0,
            limit=10,
        )

        logger.info(
            f"niconico_user[remote_niconico_user_id={niconico_user.remote_niconico_user_id}]: "
            f"Fetched the latest {len(user_broadcast_programs)} live programs"
        )

        upsert_objects: list[LiveInboxApiNiconicoLiveProgramUpsertObject] = []
        for program in user_broadcast_programs:
            logger.info(
                f"{program.niconico_content_id}: {program.title} "
                f"[{program.start_time} - {program.end_time}]"
            )

            upsert_objects.append(
                LiveInboxApiNiconicoLiveProgramUpsertObject(
                    remote_niconico_content_id=program.niconico_content_id,
                    remote_niconico_user_id=program.niconico_user_id,
                    title=program.title,
                    status=program.status,
                    last_fetch_time=fetch_time,
                    start_time=program.start_time,
                    end_time=program.end_time,
                ),
            )

        niconico_live_program_manager.upsert_all(
            upsert_objects=upsert_objects,
        )

        time.sleep(1)


class SubcommandUpdateArguments(BaseModel):
    live_inbox_hasura_url: str
    live_inbox_hasura_token: str
    niconico_user_icon_dir: Path
    useragent: str


def subcommand_update(args: SubcommandUpdateArguments):
    live_inbox_hasura_url = args.live_inbox_hasura_url
    live_inbox_hasura_token = args.live_inbox_hasura_token
    niconico_user_icon_dir = args.niconico_user_icon_dir
    useragent = args.useragent

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

    niconico_user_icon_cache_storage_manager = (
        LiveInboxApiNiconicoUserIconCacheStorageFileManager(
            niconico_user_icon_dir=niconico_user_icon_dir,
        )
    )

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

    fetch_uncached_niconico_user_icons(
        niconico_user_manager=niconico_user_manager,
        niconico_user_icon_client=niconico_user_icon_client,
        niconico_user_icon_cache_storage_manager=niconico_user_icon_cache_storage_manager,
        niconico_user_icon_cache_metadata_manager=niconico_user_icon_cache_metadata_manager,
    )

    update_niconico_live_programs(
        niconico_user_manager=niconico_user_manager,
        niconico_user_broadcast_history_client=niconico_user_broadcast_history_client,
        niconico_live_program_manager=niconico_live_program_manager,
    )


def execute_subcommand_update(
    args: Namespace,
):
    live_inbox_hasura_url: str = args.live_inbox_hasura_url
    live_inbox_hasura_token: str = args.live_inbox_hasura_token
    niconico_user_icon_dir: Path = args.niconico_user_icon_dir
    useragent: str = args.useragent

    subcommand_update(
        args=SubcommandUpdateArguments(
            live_inbox_hasura_url=live_inbox_hasura_url,
            live_inbox_hasura_token=live_inbox_hasura_token,
            niconico_user_icon_dir=niconico_user_icon_dir,
            useragent=useragent,
        ),
    )


def add_arguments_subcommand_update(
    parser: ArgumentParser,
    app_config: AppConfig,
):
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
        "--niconico_user_icon_dir",
        type=Path,
        default=app_config.niconico_user_icon_dir,
        required=app_config.niconico_user_icon_dir is None,
    )
    parser.add_argument(
        "--useragent",
        type=str,
        default=app_config.useragent,
        required=app_config.useragent is None,
    )

    parser.set_defaults(handler=execute_subcommand_update)
