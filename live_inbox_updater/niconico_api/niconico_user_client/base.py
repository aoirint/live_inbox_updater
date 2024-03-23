from abc import ABC, abstractmethod
from typing import Iterable

from pydantic import BaseModel


class NiconicoApiNiconicoUser(BaseModel):
    remote_niconico_user_id: str
    name: str
    icon_url: str


class NiconicoApiNiconicoUserClient(ABC):
    @abstractmethod
    def get_all(
        self,
        remote_niconico_user_ids: Iterable[str],
    ) -> Iterable[NiconicoApiNiconicoUser]: ...
