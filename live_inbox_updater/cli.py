import os
from argparse import ArgumentParser

from dotenv import load_dotenv

from .live_inbox_hasura_api.niconico_user_api import fetch_enabled_niconico_users


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

    print(
        fetch_enabled_niconico_users(
            hasura_url=live_inbox_hasura_url,
            hasura_token=live_inbox_hasura_token,
            useragent=useragent,
        ),
    )
