import hashlib
import time
import uuid
from datetime import datetime, timezone
from logging import getLogger

from ..live_inbox_api.niconico_user_icon_cache_metadata_manager import (
    LiveInboxApiNiconicoUserIconCacheMetadataManager,
)
from ..live_inbox_api.niconico_user_icon_cache_storage_manager import (
    LiveInboxApiNiconicoUserIconCacheStorageManager,
)
from ..live_inbox_api.niconico_user_manager import LiveInboxApiNiconicoUserManager
from ..niconico_api.niconico_user_icon_client import NiconicoApiNiconicoUserIconClient

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
