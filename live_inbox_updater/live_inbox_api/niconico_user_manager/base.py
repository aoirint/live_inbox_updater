from abc import ABC, abstractmethod

from pydantic import BaseModel


class LiveInboxApiNiconicoUser(BaseModel):
    remote_niconico_user_id: str
    name: str
    enabled: bool
    icon_url: str | None


class LiveInboxApiNiconicoUserManager(ABC):
    @abstractmethod
    def get_all(
        self,
    ) -> list[LiveInboxApiNiconicoUser]:
        ...
