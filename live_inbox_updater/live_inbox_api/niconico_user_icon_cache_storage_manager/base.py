from abc import ABC, abstractmethod


class LiveInboxApiNiconicoUserIconCacheStorageManager(ABC):
    @abstractmethod
    def check_exists(
        self,
        file_key: str,
        content_type: str,
    ) -> bool:
        ...

    @abstractmethod
    def save(
        self,
        file_key: str,
        content_type: str,
        content: bytes,
    ) -> None:
        ...
