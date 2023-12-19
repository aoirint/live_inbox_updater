from logging import getLogger

from ..live_inbox_api.niconico_live_program_manager import (
    LiveInboxApiNiconicoLiveProgramManager,
)
from ..live_inbox_api.niconico_user_icon_cache_metadata_manager import (
    LiveInboxApiNiconicoUserIconCacheMetadataManager,
)
from ..live_inbox_api.niconico_user_icon_cache_storage_manager import (
    LiveInboxApiNiconicoUserIconCacheStorageManager,
)
from ..live_inbox_api.niconico_user_manager import LiveInboxApiNiconicoUserManager
from ..niconico_api.niconico_user_broadcast_history_client import (
    NiconicoApiNiconicoUserBroadcastHistoryClient,
)
from ..niconico_api.niconico_user_icon_client import NiconicoApiNiconicoUserIconClient
from .fetch_uncached_niconico_user_icons import fetch_uncached_niconico_user_icons
from .update_niconico_live_programs import update_niconico_live_programs

logger = getLogger(__name__)


def update_job(
    niconico_user_manager: LiveInboxApiNiconicoUserManager,
    niconico_user_icon_client: NiconicoApiNiconicoUserIconClient,
    niconico_user_icon_cache_storage_manager: LiveInboxApiNiconicoUserIconCacheStorageManager,
    niconico_user_icon_cache_metadata_manager: LiveInboxApiNiconicoUserIconCacheMetadataManager,
    niconico_user_broadcast_history_client: NiconicoApiNiconicoUserBroadcastHistoryClient,
    niconico_live_program_manager: LiveInboxApiNiconicoLiveProgramManager,
) -> None:
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
