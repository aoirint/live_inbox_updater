import os

from pydantic import BaseModel


class AppConfig(BaseModel):
    live_inbox_hasura_url: str | None
    live_inbox_hasura_token: str | None
    niconico_user_icon_dir: str | None
    useragent: str | None


def load_app_config_from_env():
    live_inbox_hasura_url = os.environ.get("LIVE_INBOX_HASURA_URL") or None
    live_inbox_hasura_token = os.environ.get("LIVE_INBOX_HASURA_TOKEN") or None
    niconico_user_icon_dir = os.environ.get("APP_NICONICO_USER_ICON_DIR") or None
    useragent = os.environ.get("APP_USERAGENT") or None

    return AppConfig(
        live_inbox_hasura_url=live_inbox_hasura_url,
        live_inbox_hasura_token=live_inbox_hasura_token,
        niconico_user_icon_dir=niconico_user_icon_dir,
        useragent=useragent,
    )
