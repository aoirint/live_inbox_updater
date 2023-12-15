from logging import getLogger
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

logger = getLogger(__name__)


class NiconicoUser(BaseModel):
    id: str
    remote_niconico_user_id: str


class GetEnabledNiconicoUserResponseData(BaseModel):
    niconico_users: list[NiconicoUser]


class GetEnabledNiconicoUserResponseBody(BaseModel):
    data: GetEnabledNiconicoUserResponseData


def fetch_enabled_niconico_users(
    hasura_url: str,
    hasura_token: str,
    useragent: str,
) -> list[NiconicoUser]:
    hasura_api_url = urljoin(hasura_url, "v1/graphql")

    payload = {
        "query": """
query GetEnabledNiconicoUsers {
  niconico_users(where: {enabled: {_eq: true}}) {
    id
    remote_niconico_user_id
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
        response_body = GetEnabledNiconicoUserResponseBody.model_validate(
            response_body_json
        )
    except ValidationError:
        logger.error(response_body_json)
        raise

    return response_body.data.niconico_users
