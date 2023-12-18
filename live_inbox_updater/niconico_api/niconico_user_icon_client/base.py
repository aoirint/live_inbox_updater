from abc import ABC, abstractmethod

from pydantic import BaseModel


class NiconicoApiNiconicoUserIcon(BaseModel):
    url: str
    content_type: str
    content: bytes


class NiconicoApiNiconicoUserIconClient(ABC):
    @abstractmethod
    def get(
        self,
        url: str,
    ) -> NiconicoApiNiconicoUserIcon:
        ...
