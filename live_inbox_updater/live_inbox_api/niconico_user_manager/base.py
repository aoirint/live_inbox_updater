from abc import ABC, abstractmethod
from typing import Iterable

from pydantic import BaseModel


class LiveInboxApiNiconicoUser(BaseModel):
    remote_niconico_user_id: str
    name: str
    enabled: bool
    icon_url: str | None


class LiveInboxApiNiconicoUserCreateObject(BaseModel):
    remote_niconico_user_id: str
    name: str
    enabled: bool
    icon_url: str | None


class LiveInboxApiNiconicoUserEnabledUpdateObject(BaseModel):
    remote_niconico_user_id: str
    enabled: bool


class LiveInboxApiNiconicoUserManager(ABC):
    @abstractmethod
    def get_all(
        self,
    ) -> list[LiveInboxApiNiconicoUser]: ...

    @abstractmethod
    def create_users(
        self,
        create_objects: Iterable[LiveInboxApiNiconicoUserCreateObject],
    ) -> None: ...

    @abstractmethod
    def bulk_update_user_enabled(
        self,
        update_objects: Iterable[LiveInboxApiNiconicoUserEnabledUpdateObject],
    ) -> None: ...
