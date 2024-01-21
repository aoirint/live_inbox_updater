import logging
from argparse import ArgumentParser
from logging import getLogger

from dotenv import load_dotenv

from . import __version__ as APP_VERSION
from .app_config import load_app_config_from_env
from .subcommand.subcommand_add_user import add_arguments_subcommand_add_user
from .subcommand.subcommand_disable_user import add_arguments_subcommand_disable_user
from .subcommand.subcommand_enable_user import add_arguments_subcommand_enable_user
from .subcommand.subcommand_update import add_arguments_subcommand_update

logger = getLogger(__name__)


def main() -> None:
    load_dotenv()
    app_config = load_app_config_from_env()

    parser = ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version=APP_VERSION,
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
    )

    subparsers = parser.add_subparsers()

    subparser_update = subparsers.add_parser("update")
    add_arguments_subcommand_update(
        parser=subparser_update,
        app_config=app_config,
    )

    subparser_disable_user = subparsers.add_parser("disable_user")
    add_arguments_subcommand_disable_user(
        parser=subparser_disable_user,
        app_config=app_config,
    )

    subparser_enable_user = subparsers.add_parser("enable_user")
    add_arguments_subcommand_enable_user(
        parser=subparser_enable_user,
        app_config=app_config,
    )

    subparser_add_user = subparsers.add_parser("add_user")
    add_arguments_subcommand_add_user(
        parser=subparser_add_user,
        app_config=app_config,
    )

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()
