import httpx
from pydantic import BaseModel, Field


class UserApiResponseMeta(BaseModel):
    status: int


class UserIconsUrls(BaseModel):
    uri150x150: Field(alias="150x150")


class UserIcons(BaseModel):
    urls: UserIconsUrls


class User(BaseModel):
    id: str
    icons: UserIcons


class UserApiResponse(BaseModel):
    meta: UserApiResponseMeta
    data: list[User]


def fetch_users(
    user_ids: list[str],
    useragent: str,
) -> UserApiResponse:
    api_url = "https://account.nicovideo.jp/api/public/v1/users.json"

    params = {
        "userIds": user_ids,
    }
    res = httpx.get(
        url=api_url,
        params=params,
        headers={
            "User-Agent": useragent,
        },
    )
    res.raise_for_status()

    return UserApiResponse.model_validate(res.json())


class UserIconUrl(BaseModel):
    user_id: str
    icon_url: str


def fetch_user_icon_urls(
    user_ids: list[str],
    useragent: str,
) -> list[UserIconUrl]:
    users_response = fetch_users(
        user_ids=user_ids,
        useragent=useragent,
    )

    user_icon_urls: list[UserIconUrl] = []
    for user in users_response.data:
        user_icon_urls.append(
            UserIconUrl(
                user_id=user.id,
                icon_url=user.icons.urls.uri150x150,
            )
        )

    return user_icon_urls
