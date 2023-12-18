from logging import getLogger
from typing import Iterable

import httpx
from pydantic import BaseModel, Field, ValidationError

from .base import NiconicoApiNiconicoUser, NiconicoApiNiconicoUserClient

logger = getLogger(__name__)


class UserApiResponseMeta(BaseModel):
    status: int


class UserIconsUrls(BaseModel):
    uri150x150 = Field(alias="150x150")


class UserIcons(BaseModel):
    urls: UserIconsUrls


class User(BaseModel):
    userId: str
    nickname: str
    icons: UserIcons


class UserApiResponse(BaseModel):
    meta: UserApiResponseMeta
    data: list[User]


class NiconicoApiNiconicoUserNiconicoClient(NiconicoApiNiconicoUserClient):
    def __init__(
        self,
        useragent: str,
    ):
        self.useragent = useragent

    def get_all(
        self,
        remote_niconico_user_ids: Iterable[str],
    ) -> Iterable[NiconicoApiNiconicoUser]:
        useragent = self.useragent

        remote_niconico_user_ids_list = list(remote_niconico_user_ids)
        if len(remote_niconico_user_ids_list) > 10:
            raise ValueError("Too many users given. Required num <= 10.")

        api_url = "https://account.nicovideo.jp/api/public/v1/users.json"

        params = {
            "userIds": remote_niconico_user_ids_list,
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
            response_body = UserApiResponse.model_validate(response_body_json)
        except ValidationError:
            logger.error(response_body_json)
            raise

        user_icon_urls: list[NiconicoApiNiconicoUser] = []
        for user in response_body.data:
            user_icon_urls.append(
                NiconicoApiNiconicoUser(
                    remote_niconico_user_id=user.userId,
                    name=user.nickname,
                    icon_url=user.icons.urls.uri150x150,
                ),
            )

        return user_icon_urls
