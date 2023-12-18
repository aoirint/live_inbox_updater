from urllib.parse import urlparse

import httpx

from .base import NiconicoUserIcon, NiconicoUserIconClient


class NiconicoUserIconNiconicoClient(NiconicoUserIconClient):
    def __init__(
        self,
        useragent: str,
    ):
        self.useragent = useragent

    def __validate_url(
        self,
        url: str,
    ) -> None:
        urlp = urlparse(url)

        if urlp.scheme != "https":
            raise ValueError(f"Invalid scheme: {urlp.scheme}")

        if urlp.hostname != "secure-dcdn.cdn.nimg.jp":
            raise ValueError(f"Invalid hostname: {urlp.hostname}")

    def get(
        self,
        url: str,
    ) -> NiconicoUserIcon:
        useragent = self.useragent

        self.__validate_url(url=url)

        res = httpx.get(
            url,
            headers={
                "User-Agent": useragent,
            },
        )
        res.raise_for_status()

        content_type = res.headers.get("Content-Type")
        if content_type is None:
            raise Exception("Invalid response: No Content-Type response header")

        content = res.content

        return NiconicoUserIcon(
            content_type=content_type,
            content=content,
        )
