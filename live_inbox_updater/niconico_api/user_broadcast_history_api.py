import httpx
from pydantic import BaseModel


class UserBroadcastHistoryMeta(BaseModel):
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
    screenshot: UserBroadcastHistoryProgramThumbnailScreenshot


class UserBroadcastHistoryProgramItem(BaseModel):
    id: UserBroadcastHistoryProgramId
    program: UserBroadcastHistoryProgram
    programProvider: UserBroadcastHistoryProgramProvider
    socialGroup: UserBroadcastHistoryProgramSocialGroup
    thumbnail: UserBroadcastHistoryProgramThumbnail
    linkedContent: UserBroadcastHistoryProgramLinkedContent | None = None


class UserBroadcastHistoryData(BaseModel):
    totalCount: int | None = None
    hasNext: bool | None = None
    programsList: list[UserBroadcastHistoryProgramItem]


class UserBroadcastHistory(BaseModel):
    meta: UserBroadcastHistoryMeta
    data: UserBroadcastHistoryData


def fetch_user_broadcast_history_string(
    provider_type: str,
    provider_id: str,
    useragent: str,
    is_include_non_public: bool = False,
    offset: int = 0,
    limit: int = 100,
    with_total_count: bool = True,
) -> str:
    api_url = "https://live.nicovideo.jp/front/api/v1/user-broadcast-history"
    params = {
        "providerType": provider_type,
        "providerId": provider_id,
        "isIncludeNonPublic": "true" if is_include_non_public else "false",
        "offset": str(offset),
        "limit": str(limit),
        "withTotalCount": "true" if with_total_count else "false",
    }

    res = httpx.get(
        url=api_url,
        params=params,
        headers={
            "User-Agent": useragent,
        },
    )
    res.raise_for_status()

    return res.text


def fetch_user_broadcast_history_string_by_niconico_user_id(
    niconico_user_id: str | int,
    useragent: str,
    is_include_non_public: bool = False,
    offset: int = 0,
    limit: int = 100,
    with_total_count: bool = True,
) -> str:
    return fetch_user_broadcast_history_string(
        provider_type="user",
        provider_id=str(niconico_user_id),
        useragent=useragent,
        is_include_non_public=is_include_non_public,
        offset=offset,
        limit=limit,
        with_total_count=with_total_count,
    )


def parse_user_broadcast_history_string(
    string: str,
) -> UserBroadcastHistory:
    return UserBroadcastHistory.model_validate_json(string)
