from datetime import datetime
from logging import getLogger
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

from .base import NiconicoUserIconCacheMetadataManager

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


class NiconicoUserIconCacheMetadataHasuraManager(NiconicoUserIconCacheMetadataManager):
    def __init__(
        self,
        hasura_url: str,
        hasura_token: str,
        useragent: str,
    ):
        self.hasura_url = hasura_url
        self.hasura_token = hasura_token
        self.useragent = useragent

    def save(
        self,
        url: str,
        fetched_at: datetime,
        file_size: int,
        hash_md5: str,
        content_type: str,
        file_key: str,
    ) -> None:
        hasura_url = self.hasura_url
        hasura_token = self.hasura_token
        useragent = self.useragent

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
            "variables": InsertNiconicoUserIconRequestVariables(
                url=url,
                fetched_at=fetched_at,
                file_size=file_size,
                hash_md5=hash_md5,
                content_type=content_type,
                file_key=file_key,
            ).model_dump(mode="json"),
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

        id = response_body.data.insert_niconico_user_icon_caches_one.id
        logger.info(f"Created niconico_user_icon_caches[id={id}]")
