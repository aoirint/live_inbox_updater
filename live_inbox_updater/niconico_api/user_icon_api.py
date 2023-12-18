import httpx
from pydantic import BaseModel


class NiconicoUserIcon(BaseModel):
    content_type: str
    content: bytes


def fetch_niconico_user_icon(
    icon_url: str,
    useragent: str,
) -> NiconicoUserIcon:
    res = httpx.get(
        icon_url,
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
