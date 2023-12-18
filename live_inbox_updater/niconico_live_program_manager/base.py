from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable


class NiconicoLiveProgramUpsertObject(ABC):
    remote_niconico_content_id: str
    niconico_user_id: str
    title: str
    status: str
    last_fetch_time: datetime
    start_time: datetime | None
    end_time: datetime | None


class NiconicoLiveProgramManager(ABC):
    @abstractmethod
    def upsert_all(
        self,
        upsert_objects: Iterable[NiconicoLiveProgramUpsertObject],
    ) -> None:
        ...
