import time
from datetime import datetime, timezone
from logging import getLogger

from ..live_inbox_api.niconico_live_program_manager import (
    LiveInboxApiNiconicoLiveProgramManager,
    LiveInboxApiNiconicoLiveProgramUpsertObject,
)
from ..live_inbox_api.niconico_user_manager import LiveInboxApiNiconicoUserManager
from ..niconico_api.niconico_user_broadcast_history_client import (
    NiconicoApiNiconicoUserBroadcastHistoryClient,
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
