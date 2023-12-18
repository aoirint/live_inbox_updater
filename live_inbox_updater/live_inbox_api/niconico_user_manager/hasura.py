from logging import getLogger
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

from .base import NiconicoUser, NiconicoUserManager

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


class NiconicoUserHasuraManager(NiconicoUserManager):
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
    ) -> list[NiconicoUser]:
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

        niconico_users: list[NiconicoUser] = []
        for hasura_niconico_user in hasura_niconico_users:
            niconico_users.append(
                NiconicoUser(
                    remote_niconico_user_id=hasura_niconico_user.remote_niconico_user_id,
                    name=hasura_niconico_user.name,
                    enabled=hasura_niconico_user.enabled,
                    icon_url=hasura_niconico_user.icon_url,
                ),
            )

        return niconico_users
