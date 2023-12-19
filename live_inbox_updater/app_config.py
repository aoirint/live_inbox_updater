import os
from pathlib import Path

from pydantic import BaseModel

from . import __VERSION__ as APP_VERSION


class AppConfig(BaseModel):
    live_inbox_hasura_url: str | None
    live_inbox_hasura_token: str | None
    niconico_user_icon_dir: Path | None
    useragent: str
    update_interval: int | None


def load_app_config_from_env() -> AppConfig:
    live_inbox_hasura_url = os.environ.get("LIVE_INBOX_HASURA_URL") or None
    live_inbox_hasura_token = os.environ.get("LIVE_INBOX_HASURA_TOKEN") or None
    niconico_user_icon_dir_string = os.environ.get("APP_NICONICO_USER_ICON_DIR") or None
    useragent = os.environ.get("APP_USERAGENT") or None
    update_interval_string = os.environ.get("APP_UPDATE_INTERVAL") or None

    niconico_user_icon_dir: Path | None = None
    if niconico_user_icon_dir_string is not None:
        niconico_user_icon_dir = Path(niconico_user_icon_dir_string)

    if useragent is None:
        useragent = f"LiveInboxBot/{APP_VERSION}"

    update_interval: int | None = None
    if update_interval_string is not None:
        update_interval = int(update_interval_string)

    return AppConfig(
        live_inbox_hasura_url=live_inbox_hasura_url,
        live_inbox_hasura_token=live_inbox_hasura_token,
        niconico_user_icon_dir=niconico_user_icon_dir,
        useragent=useragent,
        update_interval=update_interval,
    )
