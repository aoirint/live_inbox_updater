from argparse import ArgumentParser

from live_inbox_updater.niconico_api.user_broadcast_history_api import (
    fetch_user_broadcast_history_string_by_niconico_user_id,
    parse_user_broadcast_history_string,
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

    user_broadcast_history_string = (
        fetch_user_broadcast_history_string_by_niconico_user_id(
            niconico_user_id=niconico_user_id,
            useragent=useragent,
            offset=0,
            limit=10,
            with_total_count=True,
        )
    )
    user_broadcast_history = parse_user_broadcast_history_string(
        string=user_broadcast_history_string,
    )

    print(user_broadcast_history)
