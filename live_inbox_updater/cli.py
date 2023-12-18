import hashlib
import logging
import os
import time
import uuid
from argparse import ArgumentParser
from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path

from dotenv import load_dotenv

from .live_inbox_hasura_api.niconico_live_program_api import (
    NiconicoLiveProgramUpsertObject,
    upsert_niconico_live_programs,
)
from .live_inbox_hasura_api.niconico_user_api import fetch_enabled_niconico_users
from .niconico_api.user_broadcast_history_api import (
    fetch_user_broadcast_history_string_by_niconico_user_id,
    parse_user_broadcast_history_string,
)
from .niconico_user_icon_cache_metadata_manager import (
    NiconicoUserIconCacheMetadataHasuraManager,
    NiconicoUserIconCacheMetadataManager,
)
from .niconico_user_icon_cache_storage_manager import (
    NiconicoUserIconCacheStorageFileManager,
    NiconicoUserIconCacheStorageManager,
)
from .niconico_user_icon_client import (
    NiconicoUserIconClient,
    NiconicoUserIconNiconicoClient,
)
from .niconico_user_manager import NiconicoUserHasuraManager, NiconicoUserManager

logger = getLogger(__name__)


def fetch_uncached_niconico_user_icons(
    niconico_user_manager: NiconicoUserManager,
    niconico_user_icon_client: NiconicoUserIconClient,
    niconico_user_icon_cache_metadata_manager: NiconicoUserIconCacheMetadataManager,
    niconico_user_icon_cache_storage_manager: NiconicoUserIconCacheStorageManager,
) -> None:
    """
    未取得のユーザアイコンを取得する
    """

    # ユーザアイコンURLリストを取得
    niconico_users = niconico_user_manager.get_all()
    enabled_niconico_users = filter(
        lambda niconico_user: niconico_user.enabled, niconico_users
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


def update_niconico_broadcast_programs(
    live_inbox_hasura_url: str,
    live_inbox_hasura_token: str,
    useragent: str,
) -> None:
    niconico_users = fetch_enabled_niconico_users(
        hasura_url=live_inbox_hasura_url,
        hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )

    logger.info(f"Found {len(niconico_users)} enabled niconico_users")
    for niconico_user in niconico_users:
        logger.info(
            f"niconico_user[remote_niconico_user_id={niconico_user.remote_niconico_user_id}]: "
            "Updating live programs"
        )

        fetch_time = datetime.now(tz=timezone.utc)
        user_broadcast_history_string = (
            fetch_user_broadcast_history_string_by_niconico_user_id(
                niconico_user_id=niconico_user.remote_niconico_user_id,
                useragent=useragent,
                offset=0,
                limit=10,
                with_total_count=True,
            )
        )

        user_broadcast_history = parse_user_broadcast_history_string(
            string=user_broadcast_history_string,
        )

        logger.info(
            f"niconico_user[remote_niconico_user_id={niconico_user.remote_niconico_user_id}]: "
            f"Fetched the latest {len(user_broadcast_history.data.programsList)} live programs"
        )

        upsert_objects: list[NiconicoLiveProgramUpsertObject] = []
        for program_item in user_broadcast_history.data.programsList:
            remote_niconico_content_id = program_item.id.value

            start_time: datetime | None = None
            if program_item.program.schedule.beginTime is not None:
                start_time = datetime.fromtimestamp(
                    program_item.program.schedule.beginTime.seconds,
                    tz=timezone.utc,
                )

            end_time: datetime | None = None
            if program_item.program.schedule.endTime is not None:
                end_time = datetime.fromtimestamp(
                    program_item.program.schedule.endTime.seconds,
                    tz=timezone.utc,
                )

            start_time_string = start_time.isoformat() if start_time is not None else ""
            end_time_string = end_time.isoformat() if end_time is not None else ""
            logger.info(
                f"{remote_niconico_content_id}: {program_item.program.title} "
                f"[{start_time_string} - {end_time_string}]"
            )

            upsert_objects.append(
                NiconicoLiveProgramUpsertObject(
                    remote_niconico_content_id=remote_niconico_content_id,
                    niconico_user_id=niconico_user.id,
                    title=program_item.program.title,
                    status=program_item.program.schedule.status,
                    last_fetch_time=fetch_time,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        upsert_niconico_live_programs(
            objects=upsert_objects,
            hasura_url=live_inbox_hasura_url,
            hasura_token=live_inbox_hasura_token,
            useragent=useragent,
        )

        time.sleep(1)


def main() -> None:
    load_dotenv()

    default_live_inbox_hasura_url = os.environ.get("LIVE_INBOX_HASURA_URL") or None
    default_live_inbox_hasura_token = os.environ.get("LIVE_INBOX_HASURA_TOKEN") or None
    default_niconico_user_icon_dir = (
        os.environ.get("APP_NICONICO_USER_ICON_DIR") or None
    )

    parser = ArgumentParser()

    parser.add_argument(
        "--live_inbox_hasura_url",
        type=str,
        default=default_live_inbox_hasura_url,
        required=default_live_inbox_hasura_url is None,
    )
    parser.add_argument(
        "--live_inbox_hasura_token",
        type=str,
        default=default_live_inbox_hasura_token,
        required=default_live_inbox_hasura_token is None,
    )
    parser.add_argument(
        "--niconico_user_icon_dir",
        type=Path,
        default=default_niconico_user_icon_dir,
        required=default_niconico_user_icon_dir is None,
    )
    parser.add_argument(
        "--useragent",
        type=str,
        default="LiveInboxBot/0.0.0",
    )

    args = parser.parse_args()

    live_inbox_hasura_url: str = args.live_inbox_hasura_url
    live_inbox_hasura_token: str = args.live_inbox_hasura_token
    niconico_user_icon_dir: Path = args.niconico_user_icon_dir
    useragent: str = args.useragent

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
    )

    niconico_user_manager = NiconicoUserHasuraManager(
        hasura_url=live_inbox_hasura_url,
        hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )
    niconico_user_icon_client = NiconicoUserIconNiconicoClient(
        useragent=useragent,
    )
    niconico_user_icon_cache_metadata_manager = (
        NiconicoUserIconCacheMetadataHasuraManager(
            hasura_url=live_inbox_hasura_url,
            hasura_token=live_inbox_hasura_token,
            useragent=useragent,
        )
    )
    niconico_user_icon_cache_storage_manager = NiconicoUserIconCacheStorageFileManager(
        niconico_user_icon_dir=niconico_user_icon_dir,
    )

    fetch_uncached_niconico_user_icons(
        niconico_user_manager=niconico_user_manager,
        niconico_user_icon_client=niconico_user_icon_client,
        niconico_user_icon_cache_storage_manager=niconico_user_icon_cache_storage_manager,
        niconico_user_icon_cache_metadata_manager=niconico_user_icon_cache_metadata_manager,
    )

    update_niconico_broadcast_programs(
        live_inbox_hasura_url=live_inbox_hasura_url,
        live_inbox_hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )
