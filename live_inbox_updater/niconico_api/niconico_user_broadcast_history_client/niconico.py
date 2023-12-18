from datetime import datetime, timezone
from logging import getLogger

import httpx
from pydantic import BaseModel, ValidationError

from .base import (
    NiconicoApiNiconicoUserBroadcastHistoryClient,
    NiconicoApiNiconicoUserBroadcastProgram,
)

logger = getLogger(__name__)


class UserBroadcastHistoryResponseMeta(BaseModel):
    status: int


class UserBroadcastHistoryProgramLinkedContent(BaseModel):
    linkType: int
    contentId: str


class UserBroadcastHistoryProgramId(BaseModel):
    value: str


class UserBroadcastHistoryProgramScheduleTime(BaseModel):
    seconds: int
    nanos: int


class UserBroadcastHistoryProgramSchedule(BaseModel):
    status: str
    openTime: UserBroadcastHistoryProgramScheduleTime | None
    beginTime: UserBroadcastHistoryProgramScheduleTime | None
    scheduledEndTime: UserBroadcastHistoryProgramScheduleTime | None
    endTime: UserBroadcastHistoryProgramScheduleTime | None
    vposBaseTime: UserBroadcastHistoryProgramScheduleTime


class UserBroadcastHistoryProgram(BaseModel):
    title: str
    description: str
    schedule: UserBroadcastHistoryProgramSchedule


class UserBroadcastHistoryProgramProviderId(BaseModel):
    value: str


class UserBroadcastHistoryProgramProviderIcons(BaseModel):
    uri150x150: str


class UserBroadcastHistoryProgramProvider(BaseModel):
    type: str
    name: str
    programProviderId: UserBroadcastHistoryProgramProviderId
    icons: UserBroadcastHistoryProgramProviderIcons


class UserBroadcastHistoryProgramSocialGroup(BaseModel):
    type: str
    socialGroupId: str
    name: str
    description: str
    thumbnail: str


class UserBroadcastHistoryProgramThumbnailScreenshot(BaseModel):
    large: str


class UserBroadcastHistoryProgramThumbnail(BaseModel):
    screenshot: UserBroadcastHistoryProgramThumbnailScreenshot | None = None


class UserBroadcastHistoryProgramItem(BaseModel):
    id: UserBroadcastHistoryProgramId
    program: UserBroadcastHistoryProgram
    programProvider: UserBroadcastHistoryProgramProvider
    socialGroup: UserBroadcastHistoryProgramSocialGroup
    thumbnail: UserBroadcastHistoryProgramThumbnail
    linkedContent: UserBroadcastHistoryProgramLinkedContent | None = None


class UserBroadcastHistoryResponseData(BaseModel):
    totalCount: int | None = None
    hasNext: bool | None = None
    programsList: list[UserBroadcastHistoryProgramItem]


class UserBroadcastHistoryResponseBody(BaseModel):
    meta: UserBroadcastHistoryResponseMeta
    data: UserBroadcastHistoryResponseData


class NiconicoApiNiconicoUserBroadcastHistoryNiconicoClient(
    NiconicoApiNiconicoUserBroadcastHistoryClient
):
    def __init__(
        self,
        useragent: str,
    ):
        self.useragent = useragent

    def get_programs(
        self,
        niconico_user_id: str,
        offset: int = 0,
        limit: int = 10,
    ) -> list[NiconicoApiNiconicoUserBroadcastProgram]:
        useragent = self.useragent

        api_url = "https://live.nicovideo.jp/front/api/v1/user-broadcast-history"
        params = {
            "providerType": "user",
            "providerId": niconico_user_id,
            "isIncludeNonPublic": "false",
            "offset": str(offset),
            "limit": str(limit),
            "withTotalCount": "true",
        }

        res = httpx.get(
            url=api_url,
            params=params,
            headers={
                "User-Agent": useragent,
            },
        )
        res.raise_for_status()

        response_body_json = res.json()
        try:
            response_body = UserBroadcastHistoryResponseBody.model_validate(
                response_body_json
            )
        except ValidationError:
            logger.error(response_body_json)
            raise

        niconico_user_broadcast_programs: list[
            NiconicoApiNiconicoUserBroadcastProgram
        ] = []
        for program_item in response_body.data.programsList:
            niconico_content_id = program_item.id.value
            title = program_item.program.title
            description = program_item.program.description
            status = program_item.program.schedule.status
            niconico_user_id = program_item.programProvider.programProviderId.value

            start_time: datetime | None = None
            if program_item.program.schedule.beginTime is not None:
                start_time = datetime.fromtimestamp(
                    program_item.program.schedule.beginTime.seconds,
                    tz=timezone.utc,
                )

            end_time: datetime | None = None
            if program_item.program.schedule.endTime is not None:
                end_time = datetime.fromtimestamp(
                    program_item.program.schedule.endTime.seconds,
                    tz=timezone.utc,
                )

            niconico_user_broadcast_programs.append(
                NiconicoApiNiconicoUserBroadcastProgram(
                    niconico_content_id=niconico_content_id,
                    title=title,
                    description=description,
                    status=status,
                    niconico_user_id=niconico_user_id,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        return niconico_user_broadcast_programs
