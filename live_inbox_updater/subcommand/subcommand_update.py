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
)
from ..live_inbox_api.niconico_user_manager import NiconicoUserHasuraManager
from ..live_inbox_utility import update_job
from ..niconico_api.niconico_user_broadcast_history_client import (
    NiconicoApiNiconicoUserBroadcastHistoryNiconicoClient,
)
from ..niconico_api.niconico_user_icon_client import (
    NiconicoApiNiconicoUserIconNiconicoClient,
)

logger = getLogger(__name__)


class SubcommandUpdateArguments(BaseModel):
    live_inbox_hasura_url: str
    live_inbox_hasura_token: str
    niconico_user_icon_dir: Path
    useragent: str
    update_interval: int


def subcommand_update(args: SubcommandUpdateArguments) -> None:
    live_inbox_hasura_url = args.live_inbox_hasura_url
    live_inbox_hasura_token = args.live_inbox_hasura_token
    niconico_user_icon_dir = args.niconico_user_icon_dir
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
            scheduled_time_seconds = scheduler.idle_seconds()
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
    niconico_user_icon_dir: Path = args.niconico_user_icon_dir
    useragent: str = args.useragent
    update_interval: int = args.update_interval

    subcommand_update(
        args=SubcommandUpdateArguments(
            live_inbox_hasura_url=live_inbox_hasura_url,
            live_inbox_hasura_token=live_inbox_hasura_token,
            niconico_user_icon_dir=niconico_user_icon_dir,
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
    parser.add_argument(
        "--update_interval",
        type=int,
        default=app_config.update_interval,
        required=app_config.update_interval is None,
        help="Update interval in seconds",
    )

    parser.set_defaults(handler=execute_subcommand_update)
