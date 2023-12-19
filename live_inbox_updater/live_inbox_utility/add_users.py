from ..live_inbox_api.niconico_user_manager import (
    LiveInboxApiNiconicoUserCreateObject,
    LiveInboxApiNiconicoUserManager,
)
from ..niconico_api.niconico_user_client import NiconicoApiNiconicoUserClient


def add_users(
    remote_niconico_user_ids: list[str],
    niconico_user_client: NiconicoApiNiconicoUserClient,
    niconico_user_manager: LiveInboxApiNiconicoUserManager,
) -> None:
    niconico_users = list(
        niconico_user_client.get_all(
            remote_niconico_user_ids=remote_niconico_user_ids,
        ),
    )

    create_objects: list[LiveInboxApiNiconicoUserCreateObject] = []
    for niconico_user in niconico_users:
        create_objects.append(
            LiveInboxApiNiconicoUserCreateObject(
                remote_niconico_user_id=niconico_user.remote_niconico_user_id,
                name=niconico_user.name,
                enabled=False,
                icon_url=niconico_user.icon_url,
            ),
        )

    niconico_user_manager.create_users(
        create_objects=create_objects,
    )
