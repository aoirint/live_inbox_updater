from logging import getLogger
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

logger = getLogger(__name__)


class GetEnabledNiconicoUserResponseNiconicoUserNiconicoUserIconCache(BaseModel):
    id: str


class GetEnabledNiconicoUserResponseNiconicoUser(BaseModel):
    id: str
    remote_niconico_user_id: str
    niconico_user_icon_cache: (
        GetEnabledNiconicoUserResponseNiconicoUserNiconicoUserIconCache | None
    )


class GetEnabledIconNiconicoUserResponseData(BaseModel):
    niconico_users: list[GetEnabledNiconicoUserResponseNiconicoUser]


class GetEnabledIconNiconicoUserResponseBody(BaseModel):
    data: GetEnabledIconNiconicoUserResponseData


def fetch_enabled_niconico_users(
    hasura_url: str,
    hasura_token: str,
    useragent: str,
) -> list[GetEnabledNiconicoUserResponseNiconicoUser]:
    hasura_api_url = urljoin(hasura_url, "v1/graphql")

    payload = {
        "query": """
query GetEnabledNiconicoUsers {
  niconico_users(where: {enabled: {_eq: true}}) {
    id
    remote_niconico_user_id
    niconico_user_icon_cache {
      id
    }
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
        response_body = GetEnabledIconNiconicoUserResponseBody.model_validate(
            response_body_json
        )
    except ValidationError:
        logger.error(response_body_json)
        raise

    return response_body.data.niconico_users


class GetUncachedIconNiconicoUserResponseNiconicoUser(BaseModel):
    id: str
    icon_url: str


class GetUncachedIconNiconicoUserResponseData(BaseModel):
    niconico_users: list[GetUncachedIconNiconicoUserResponseNiconicoUser]


class GetUncachedIconNiconicoUserResponseBody(BaseModel):
    data: GetUncachedIconNiconicoUserResponseData


def fetch_uncached_icon_niconico_users(
    hasura_url: str,
    hasura_token: str,
    useragent: str,
) -> list[GetUncachedIconNiconicoUserResponseNiconicoUser]:
    hasura_api_url = urljoin(hasura_url, "v1/graphql")

    payload = {
        "query": """
query GetUncachedIconNiconicoUsers {
  niconico_users(
    where: {
      enabled: {
        _eq: true
      }
      icon_url: {
        _is_null: false
      }
      _not: {
        niconico_user_icon_cache: {
        }
      }
    }
  ) {
    id
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
        response_body = GetUncachedIconNiconicoUserResponseBody.model_validate(
            response_body_json
        )
    except ValidationError:
        logger.error(response_body_json)
        raise

    return response_body.data.niconico_users
