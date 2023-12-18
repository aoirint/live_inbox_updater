from datetime import datetime
from logging import getLogger
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

logger = getLogger(__name__)


class InsertNiconicoUserIconRequestVariables(BaseModel):
    url: str
    fetched_at: datetime
    file_size: int
    hash_md5: str
    content_type: str
    file_key: str


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
  $fetched_at: timestamptz!
  $file_size: Int!
  $hash_md5: String!
  $content_type: String!
  $file_key: String!
) {
  insert_niconico_user_icon_caches_one(
    object: {
      url: $url
      fetched_at: $fetched_at
      file_size: $file_size
      hash_md5: $hash_md5
      content_type: $content_type
      file_key: $file_key
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
