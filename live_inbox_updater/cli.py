import hashlib
import logging
import os
import time
import uuid
from argparse import ArgumentParser
from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .live_inbox_hasura_api.niconico_live_program_api import (
    NiconicoLiveProgramUpsertObject,
    upsert_niconico_live_programs,
)
from .live_inbox_hasura_api.niconico_user_api import (
    fetch_enabled_niconico_users,
    fetch_uncached_icon_niconico_users,
)
from .live_inbox_hasura_api.niconico_user_icon_api import (
    InsertNiconicoUserIconRequestVariables,
    insert_niconico_user_icon_cache,
)
from .niconico_api.user_broadcast_history_api import (
    fetch_user_broadcast_history_string_by_niconico_user_id,
    parse_user_broadcast_history_string,
)
from .niconico_api.user_icon_api import fetch_niconico_user_icon

logger = getLogger(__name__)


def create_niconico_user_icon_path(
    niconico_user_icon_dir: Path,
    file_key: str,
    content_type: str,
) -> Path:
    suffix: str | None = None
    if content_type == "image/jpeg":
        suffix = ".jpg"
    elif content_type == "image/png":
        suffix = ".png"
    elif content_type == "image/gif":
        suffix = ".gif"
    else:
        raise Exception(
            f"Unsupported content_type: {content_type}",
        )

    file_name = f"{file_key}{suffix}"
    return niconico_user_icon_dir / file_name


def fetch_uncached_niconico_user_icons(
    niconico_user_icon_dir: Path,
    live_inbox_hasura_url: str,
    live_inbox_hasura_token: str,
    useragent: str,
) -> None:
    """
    未取得のユーザアイコンを取得する
    """
    niconico_user_icon_dir.mkdir(parents=True, exist_ok=True)

    # 各アカウントのアイコンキャッシュ取得状況を確認する
    uncached_icon_niconico_users = fetch_uncached_icon_niconico_users(
        hasura_url=live_inbox_hasura_url,
        hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )

    logger.info(
        f"Found uncached {len(uncached_icon_niconico_users)} niconico user icons"
    )

    for niconico_user in uncached_icon_niconico_users:
        file_key = str(uuid.uuid4())
        fetched_at = datetime.now(tz=timezone.utc)
        icon_url = niconico_user.icon_url

        niconico_user_icon = fetch_niconico_user_icon(
            icon_url=icon_url,
            useragent=useragent,
        )

        icon_path = create_niconico_user_icon_path(
            niconico_user_icon_dir=niconico_user_icon_dir,
            file_key=file_key,
            content_type=niconico_user_icon.content_type,
        )
        icon_path.parent.mkdir(parents=True, exist_ok=True)

        content = niconico_user_icon.content
        icon_path.write_bytes(content)

        file_size = len(content)
        hash_md5 = hashlib.md5(content).hexdigest()

        insert_niconico_user_icon_cache(
            obj=InsertNiconicoUserIconRequestVariables(
                url=icon_url,
                fetched_at=fetched_at,
                file_size=file_size,
                hash_md5=hash_md5,
                content_type=niconico_user_icon.content_type,
                file_key=file_key,
            ),
            hasura_url=live_inbox_hasura_url,
            hasura_token=live_inbox_hasura_token,
            useragent=useragent,
        )

    logger.info(f"Fetched {len(uncached_icon_niconico_users)} niconico user icons")


def main() -> None:
    load_dotenv()

    default_live_inbox_hasura_url = os.environ.get("LIVE_INBOX_HASURA_URL") or None
    default_live_inbox_hasura_token = os.environ.get("LIVE_INBOX_HASURA_TOKEN") or None
    default_niconico_user_icon_dir = (
        os.environ.get("APP_NICONICO_USER_ICON_DIR") or None
    )

    parser = ArgumentParser()

    parser.add_argument(
        "--live_inbox_hasura_url",
        type=str,
        default=default_live_inbox_hasura_url,
        required=default_live_inbox_hasura_url is None,
    )
    parser.add_argument(
        "--live_inbox_hasura_token",
        type=str,
        default=default_live_inbox_hasura_token,
        required=default_live_inbox_hasura_token is None,
    )
    parser.add_argument(
        "--niconico_user_icon_dir",
        type=Path,
        default=default_niconico_user_icon_dir,
        required=default_niconico_user_icon_dir is None,
    )
    parser.add_argument(
        "--useragent",
        type=str,
        default="LiveInboxBot/0.0.0",
    )

    args = parser.parse_args()

    live_inbox_hasura_url: str = args.live_inbox_hasura_url
    live_inbox_hasura_token: str = args.live_inbox_hasura_token
    niconico_user_icon_dir: Path = args.niconico_user_icon_dir
    useragent: str = args.useragent

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
    )

    fetch_uncached_niconico_user_icons(
        niconico_user_icon_dir=niconico_user_icon_dir,
        live_inbox_hasura_url=live_inbox_hasura_url,
        live_inbox_hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )

    niconico_users = fetch_enabled_niconico_users(
        hasura_url=live_inbox_hasura_url,
        hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )

    logger.info(f"Found {len(niconico_users)} enabled niconico_users")
    for niconico_user in niconico_users:
        logger.info(
            f"niconico_user[remote_niconico_user_id={niconico_user.remote_niconico_user_id}]: "
            "Updating live programs"
        )

        fetch_time = datetime.now(tz=timezone.utc)
        user_broadcast_history_string = (
            fetch_user_broadcast_history_string_by_niconico_user_id(
                niconico_user_id=niconico_user.remote_niconico_user_id,
                useragent=useragent,
                offset=0,
                limit=10,
                with_total_count=True,
            )
        )

        user_broadcast_history = parse_user_broadcast_history_string(
            string=user_broadcast_history_string,
        )

        logger.info(
            f"niconico_user[remote_niconico_user_id={niconico_user.remote_niconico_user_id}]: "
            f"Fetched the latest {len(user_broadcast_history.data.programsList)} live programs"
        )

        upsert_objects: list[NiconicoLiveProgramUpsertObject] = []
        for program_item in user_broadcast_history.data.programsList:
            remote_niconico_content_id = program_item.id.value

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

            start_time_string = start_time.isoformat() if start_time is not None else ""
            end_time_string = end_time.isoformat() if end_time is not None else ""
            logger.info(
                f"{remote_niconico_content_id}: {program_item.program.title} "
                f"[{start_time_string} - {end_time_string}]"
            )

            upsert_objects.append(
                NiconicoLiveProgramUpsertObject(
                    remote_niconico_content_id=remote_niconico_content_id,
                    niconico_user_id=niconico_user.id,
                    title=program_item.program.title,
                    status=program_item.program.schedule.status,
                    last_fetch_time=fetch_time,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        upsert_niconico_live_programs(
            objects=upsert_objects,
            hasura_url=live_inbox_hasura_url,
            hasura_token=live_inbox_hasura_token,
            useragent=useragent,
        )

        time.sleep(1)
