from datetime import datetime
from logging import getLogger
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

logger = getLogger(__name__)


class InsertNiconicoUserIconRequestVariables(BaseModel):
    url: str
    file_size: int
    hash_md5: str
    fetched_at: datetime


class InsertNiconicoUserIconCacheResponseInsertNiconicoUserIconCache(BaseModel):
    id: str


class InsertNiconicoUserIconCacheResponseData(BaseModel):
    insert_niconico_user_icon_caches_one: (
        InsertNiconicoUserIconCacheResponseInsertNiconicoUserIconCache
    )


class InsertNiconicoUserIconCacheResponseBody(BaseModel):
    data: InsertNiconicoUserIconCacheResponseData


def insert_niconico_user_icon_cache(
    obj: InsertNiconicoUserIconRequestVariables,
    hasura_url: str,
    hasura_token: str,
    useragent: str,
) -> InsertNiconicoUserIconCacheResponseBody:
    hasura_api_url = urljoin(hasura_url, "v1/graphql")

    payload = {
        "query": """
mutation InsertNiconicoUserIconCache(
  $url: String!
  $size: Int!
  $hash_md5: String!
  $fetched_at: timestamptz!
) {
  insert_niconico_user_icon_caches_one(
    object: {
      url: $url
      size: $size
      hash_md5: $hash_md5
      fetched_at: $fetched_at
    }
  ) {
    id
  }
}
""",
        "variables": obj.model_dump(mode="json"),
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
        response_body = InsertNiconicoUserIconCacheResponseBody.model_validate(
            response_body_json
        )
    except ValidationError:
        logger.error(response_body_json)
        raise

    return response_body
