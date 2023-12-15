from argparse import ArgumentParser

from .niconico_api.user_broadcast_history_api import (
    fetch_user_broadcast_history_by_niconico_user_id,
)


def main() -> None:
    parser = ArgumentParser()

    parser.add_argument(
        "--niconico_user_id",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--useragent",
        type=str,
        default="LiveInboxBot/0.0.0",
    )

    args = parser.parse_args()

    niconico_user_id: str = args.niconico_user_id
    useragent: str = args.useragent

    fetch_user_broadcast_history_by_niconico_user_id(
        niconico_user_id=niconico_user_id,
        useragent=useragent,
        offset=0,
        limit=10,
        with_total_count=True,
    )