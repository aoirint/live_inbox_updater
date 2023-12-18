from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable

from pydantic import BaseModel


class NiconicoUserIconCacheMetadata(BaseModel):
    url: str
    fetched_at: datetime
    file_size: int
    hash_md5: str
    content_type: str
    file_key: str


class NiconicoUserIconCacheMetadataManager(ABC):
    @abstractmethod
    def get_by_urls(
        self,
        urls: Iterable[str],
    ) -> list[NiconicoUserIconCacheMetadata]:
        ...

    @abstractmethod
    def save(
        self,
        url: str,
        fetched_at: datetime,
        file_size: int,
        hash_md5: str,
        content_type: str,
        file_key: str,
    ) -> None:
        ...
