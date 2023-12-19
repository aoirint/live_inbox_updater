import time
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
)
from ..live_inbox_api.niconico_user_icon_cache_storage_manager import (
    LiveInboxApiNiconicoUserIconCacheStorageFileManager,
)
from ..live_inbox_api.niconico_user_manager import (
    LiveInboxApiNiconicoUserManager,
    NiconicoUserHasuraManager,
)
from ..live_inbox_utility import fetch_uncached_niconico_user_icons
from ..niconico_api.niconico_user_broadcast_history_client import (
    NiconicoApiNiconicoUserBroadcastHistoryClient,
    NiconicoApiNiconicoUserBroadcastHistoryNiconicoClient,
)
from ..niconico_api.niconico_user_icon_client import (
    NiconicoApiNiconicoUserIconNiconicoClient,
)

logger = getLogger(__name__)


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

    # TODO: 「取得対象でなかった」かつ「statusがENDEDでない」番組を再取得して、ON_AIRの更新漏れが起きないようにする


class SubcommandUpdateArguments(BaseModel):
    live_inbox_hasura_url: str
    live_inbox_hasura_token: str
    niconico_user_icon_dir: Path
    useragent: str


def subcommand_update(args: SubcommandUpdateArguments) -> None:
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
) -> None:
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
