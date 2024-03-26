from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel


class NiconicoApiNiconicoUserBroadcastProgram(BaseModel):
    niconico_content_id: str
    title: str
    description: str
    status: str
    niconico_user_id: str
    start_time: datetime | None
    end_time: datetime | None


class NiconicoApiNiconicoUserBroadcastHistoryClient(ABC):
    @abstractmethod
    def get_programs(
        self,
        niconico_user_id: str,
        offset: int = 0,
        limit: int = 10,
    ) -> list[NiconicoApiNiconicoUserBroadcastProgram]: ...
