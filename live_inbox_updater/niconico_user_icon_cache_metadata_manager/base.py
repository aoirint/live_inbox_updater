from abc import ABC, abstractmethod
from datetime import datetime


class NiconicoUserIconCacheMetadataManager(ABC):
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
