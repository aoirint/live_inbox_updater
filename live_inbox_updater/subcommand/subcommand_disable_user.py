from argparse import ArgumentParser, Namespace
from logging import getLogger

from pydantic import BaseModel

from ..app_config import AppConfig
from ..live_inbox_api.niconico_user_manager import NiconicoUserHasuraManager
from ..live_inbox_utility import disable_users

logger = getLogger(__name__)


class SubcommandDisableUserArguments(BaseModel):
    remote_niconico_user_ids: list[str]
    live_inbox_hasura_url: str
    live_inbox_hasura_token: str
    useragent: str


def subcommand_disable_user(args: SubcommandDisableUserArguments) -> None:
    remote_niconico_user_ids = args.remote_niconico_user_ids
    live_inbox_hasura_url = args.live_inbox_hasura_url
    live_inbox_hasura_token = args.live_inbox_hasura_token
    useragent = args.useragent

    niconico_user_manager = NiconicoUserHasuraManager(
        hasura_url=live_inbox_hasura_url,
        hasura_token=live_inbox_hasura_token,
        useragent=useragent,
    )
    disable_users(
        remote_niconico_user_ids=remote_niconico_user_ids,
        niconico_user_manager=niconico_user_manager,
    )


def execute_subcommand_disable_user(
    args: Namespace,
) -> None:
    remote_niconico_user_ids: list[str] = args.remote_niconico_user_ids
    live_inbox_hasura_url: str = args.live_inbox_hasura_url
    live_inbox_hasura_token: str = args.live_inbox_hasura_token
    useragent: str = args.useragent

    subcommand_disable_user(
        args=SubcommandDisableUserArguments(
            remote_niconico_user_ids=remote_niconico_user_ids,
            live_inbox_hasura_url=live_inbox_hasura_url,
            live_inbox_hasura_token=live_inbox_hasura_token,
            useragent=useragent,
        ),
    )


def add_arguments_subcommand_disable_user(
    parser: ArgumentParser,
    app_config: AppConfig,
) -> None:
    parser.add_argument(
        "--remote_niconico_user_ids",
        type=str,
        nargs="+",
        required=True,
    )

    parser.add_argument(
        "--live_inbox_hasura_url",
        type=str,
        default=app_config.live_inbox_hasura_url,
        required=app_config.live_inbox_hasura_url is None,
    )
    parser.add_argument(
        "--live_inbox_hasura_token",
        type=str,
        default=app_config.live_inbox_hasura_token,
        required=app_config.live_inbox_hasura_token is None,
    )
    parser.add_argument(
        "--useragent",
        type=str,
        default=app_config.useragent,
        required=app_config.useragent is None,
    )

    parser.set_defaults(handler=execute_subcommand_disable_user)
