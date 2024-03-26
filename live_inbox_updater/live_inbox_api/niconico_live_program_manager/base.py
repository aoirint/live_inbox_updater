from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable

from pydantic import BaseModel


class LiveInboxApiNiconicoLiveProgramUpsertObject(BaseModel):
    remote_niconico_content_id: str
    remote_niconico_user_id: str
    title: str
    status: str
    last_fetch_time: datetime
    start_time: datetime | None
    end_time: datetime | None


class LiveInboxApiNiconicoLiveProgramManager(ABC):
    @abstractmethod
    def upsert_all(
        self,
        upsert_objects: Iterable[LiveInboxApiNiconicoLiveProgramUpsertObject],
    ) -> None: ...
