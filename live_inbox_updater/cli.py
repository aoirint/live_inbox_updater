import os
from argparse import ArgumentParser

from dotenv import load_dotenv

from .live_inbox_hasura_api.niconico_user_api import fetch_enabled_niconico_users


def main() -> None:
    load_dotenv()

    live_inbox_hasura_url = os.environ.get("LIVE_INBOX_HASURA_URL") or None
    live_inbox_hasura_token = os.environ.get("LIVE_INBOX_HASURA_TOKEN") or None

    parser = ArgumentParser()

    parser.add_argument(
        "--live_inbox_hasura_url",
        type=str,
        default=live_inbox_hasura_url,
        required=live_inbox_hasura_url is None,
    )
    parser.add_argument(
        "--live_inbox_hasura_token",
        type=str,
        default=live_inbox_hasura_token,
        required=live_inbox_hasura_token is None,
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
