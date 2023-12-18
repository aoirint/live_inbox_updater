from abc import ABC, abstractmethod

from pydantic import BaseModel


class NiconicoUserIcon(BaseModel):
    url: str
    content_type: str
    content: bytes


class NiconicoUserIconClient(ABC):
    @abstractmethod
    def get(
        self,
        url: str,
    ) -> NiconicoUserIcon:
        ...
