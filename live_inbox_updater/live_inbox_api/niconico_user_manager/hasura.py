from logging import getLogger
from typing import Iterable
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

from .base import (
    LiveInboxApiNiconicoUser,
    LiveInboxApiNiconicoUserEnabledUpdateObject,
    LiveInboxApiNiconicoUserManager,
)

logger = getLogger(__name__)


class GetNiconicoUsersResponseNiconicoUser(BaseModel):
    id: str
    remote_niconico_user_id: str
    name: str
    enabled: bool
    icon_url: str | None


class GetNiconicoUsersResponseData(BaseModel):
    niconico_users: list[GetNiconicoUsersResponseNiconicoUser]


class GetNiconicoUsersResponseBody(BaseModel):
    data: GetNiconicoUsersResponseData


class BulkUpdateNiconicoUserEnabledResponseUpdateNiconicoUsersMany(BaseModel):
    affected_rows: int


class BulkUpdateNiconicoUserEnabledResponseData(BaseModel):
    update_niconico_users_many: BulkUpdateNiconicoUserEnabledResponseUpdateNiconicoUsersMany


class BulkUpdateNiconicoUserEnabledResponseBody(BaseModel):
    data: BulkUpdateNiconicoUserEnabledResponseData


class NiconicoUserHasuraManager(LiveInboxApiNiconicoUserManager):
    def __init__(
        self,
        hasura_url: str,
        hasura_token: str,
        useragent: str,
    ):
        self.hasura_url = hasura_url
        self.hasura_token = hasura_token
        self.useragent = useragent

    def get_all(
        self,
    ) -> list[LiveInboxApiNiconicoUser]:
        hasura_url = self.hasura_url
        hasura_token = self.hasura_token
        useragent = self.useragent

        hasura_api_url = urljoin(hasura_url, "v1/graphql")

        payload = {
            "query": """
query GetNiconicoUsers {
  niconico_users {
    id
    remote_niconico_user_id
    name
    enabled
    icon_url
  }
}
""",
        }

        res = httpx.post(
            url=hasura_api_url,
            headers={
                "Authorization": f"Bearer {hasura_token}",
                "User-Agent": useragent,
            },
            json=payload,
        )
        res.raise_for_status()

        response_body_json = res.json()
        try:
            response_body = GetNiconicoUsersResponseBody.model_validate(
                response_body_json
            )
        except ValidationError:
            logger.error(response_body_json)
            raise

        hasura_niconico_users = response_body.data.niconico_users
        logger.info(f"Fetched {len(hasura_niconico_users)} niconico users")

        niconico_users: list[LiveInboxApiNiconicoUser] = []
        for hasura_niconico_user in hasura_niconico_users:
            niconico_users.append(
                LiveInboxApiNiconicoUser(
                    remote_niconico_user_id=hasura_niconico_user.remote_niconico_user_id,
                    name=hasura_niconico_user.name,
                    enabled=hasura_niconico_user.enabled,
                    icon_url=hasura_niconico_user.icon_url,
                ),
            )

        return niconico_users

    def bulk_update_user_enabled(
        self,
        update_objects: Iterable[LiveInboxApiNiconicoUserEnabledUpdateObject],
    ) -> None:
        hasura_url = self.hasura_url
        hasura_token = self.hasura_token
        useragent = self.useragent

        hasura_api_url = urljoin(hasura_url, "v1/graphql")

        updates: list[dict] = []
        for update_object in update_objects:
            updates.append(
                {
                    "_set": {
                        "enabled": update_object.enabled,
                    },
                    "_where": {
                        "remote_niconico_user_id": {
                            "_eq": update_object.remote_niconico_user_id,
                        },
                    },
                },
            )

        payload = {
            "query": """
mutation BulkUpdateNiconicoUserEnabled(
  $updates: [niconico_users_updates!]!
) {
  update_niconico_users_many(updates: $updates) {
    affected_rows
  }
}
""",
            "variables": {
                "updates": updates,
            },
        }

        res = httpx.post(
            url=hasura_api_url,
            headers={
                "Authorization": f"Bearer {hasura_token}",
                "User-Agent": useragent,
            },
            json=payload,
        )
        res.raise_for_status()

        response_body_json = res.json()
        try:
            response_body = BulkUpdateNiconicoUserEnabledResponseBody.model_validate(
                response_body_json
            )
        except ValidationError:
            logger.error(response_body_json)
            raise

        affected_rows = response_body.data.update_niconico_users_many.affected_rows
        logger.info(f"Bulk updated {len(affected_rows)} niconico user enabled")
