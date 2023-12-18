from datetime import datetime
from logging import getLogger
from typing import Iterable
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

from .base import (
    LiveInboxApiNiconicoUserIconCacheMetadata,
    LiveInboxApiNiconicoUserIconCacheMetadataManager,
)

logger = getLogger(__name__)


class GetNiconicoUserIconCacheByUrlsRequestVariables(BaseModel):
    urls: list[str]


class GetNiconicoUserIconCacheByUrlsResponseNiconicoUserIconCache(BaseModel):
    id: str
    url: str
    fetched_at: datetime
    file_size: int
    hash_md5: str
    content_type: str
    file_key: str


class GetNiconicoUserIconCacheByUrlsResponseData(BaseModel):
    niconico_user_icon_caches: (
        list[GetNiconicoUserIconCacheByUrlsResponseNiconicoUserIconCache]
    )


class GetNiconicoUserIconCacheByUrlsResponseBody(BaseModel):
    data: GetNiconicoUserIconCacheByUrlsResponseData


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


class LiveInboxApiNiconicoUserIconCacheMetadataHasuraManager(
    LiveInboxApiNiconicoUserIconCacheMetadataManager
):
    def __init__(
        self,
        hasura_url: str,
        hasura_token: str,
        useragent: str,
    ):
        self.hasura_url = hasura_url
        self.hasura_token = hasura_token
        self.useragent = useragent

    def get_by_urls(
        self,
        urls: Iterable[str],
    ) -> list[LiveInboxApiNiconicoUserIconCacheMetadata]:
        hasura_url = self.hasura_url
        hasura_token = self.hasura_token
        useragent = self.useragent

        hasura_api_url = urljoin(hasura_url, "v1/graphql")

        payload = {
            "query": """
query GetNiconicoUserIconCacheByUrls(
  $urls: [String!]!
) {
  niconico_user_icon_caches(
    where: {
      url: {
        _in: $urls
      }
    }
  ) {
    id
    url
    fetched_at
    file_size
    hash_md5
    content_type
    file_key
  }
}
""",
            "variables": GetNiconicoUserIconCacheByUrlsRequestVariables(
                urls=list(urls),
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
            response_body = GetNiconicoUserIconCacheByUrlsResponseBody.model_validate(
                response_body_json
            )
        except ValidationError:
            logger.error(response_body_json)
            raise

        hasura_niconico_user_icon_caches = response_body.data.niconico_user_icon_caches
        logger.info(
            f"Fetched {len(hasura_niconico_user_icon_caches)} niconico_user_icon_caches"
        )

        niconico_user_icon_cache_metadatas: list[
            LiveInboxApiNiconicoUserIconCacheMetadata
        ] = []
        for hasura_niconico_user_icon_cache in hasura_niconico_user_icon_caches:
            niconico_user_icon_cache_metadatas.append(
                LiveInboxApiNiconicoUserIconCacheMetadata(
                    url=hasura_niconico_user_icon_cache.url,
                    fetched_at=hasura_niconico_user_icon_cache.fetched_at,
                    file_size=hasura_niconico_user_icon_cache.file_size,
                    hash_md5=hasura_niconico_user_icon_cache.hash_md5,
                    content_type=hasura_niconico_user_icon_cache.content_type,
                    file_key=hasura_niconico_user_icon_cache.file_key,
                ),
            )

        return niconico_user_icon_cache_metadatas

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
