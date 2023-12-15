import logging
import os
import time
from argparse import ArgumentParser
from datetime import datetime, timezone
from logging import getLogger

from dotenv import load_dotenv

from .live_inbox_hasura_api.niconico_live_program_api import (
    NiconicoLiveProgramUpsertObject,
    upsert_niconico_live_programs,
)
from .live_inbox_hasura_api.niconico_user_api import fetch_enabled_niconico_users
from .niconico_api.user_broadcast_history_api import (
    fetch_user_broadcast_history_string_by_niconico_user_id,
    parse_user_broadcast_history_string,
)


def main() -> None:
    load_dotenv()

    default_live_inbox_hasura_url = os.environ.get("LIVE_INBOX_HASURA_URL") or None
    default_live_inbox_hasura_token = os.environ.get("LIVE_INBOX_HASURA_TOKEN") or None

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
        "--useragent",
        type=str,
        default="LiveInboxBot/0.0.0",
    )

    args = parser.parse_args()

    live_inbox_hasura_url: str = args.live_inbox_hasura_url
    live_inbox_hasura_token: str = args.live_inbox_hasura_token
    useragent: str = args.useragent

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
    )

    logger = getLogger(__name__)

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
                    program_item.program.schedule.beginTime.seconds, tz=timezone.utc
                )

            end_time: datetime | None = None
            if program_item.program.schedule.endTime is not None:
                end_time = datetime.fromtimestamp(
                    program_item.program.schedule.endTime.seconds, tz=timezone.utc
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
