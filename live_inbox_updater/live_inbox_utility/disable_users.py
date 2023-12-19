from ..live_inbox_api.niconico_user_manager import (
    LiveInboxApiNiconicoUserEnabledUpdateObject,
    LiveInboxApiNiconicoUserManager,
)


def disable_users(
    remote_niconico_user_ids: list[str],
    niconico_user_manager: LiveInboxApiNiconicoUserManager,
) -> None:
    update_objects: list[LiveInboxApiNiconicoUserEnabledUpdateObject] = []
    for remote_niconico_user_id in remote_niconico_user_ids:
        update_objects.append(
            LiveInboxApiNiconicoUserEnabledUpdateObject(
                remote_niconico_user_id=remote_niconico_user_id,
                enabled=False,
            ),
        )

    niconico_user_manager.bulk_update_user_enabled(
        update_objects=update_objects,
    )
