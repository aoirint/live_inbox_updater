import logging
from argparse import ArgumentParser
from logging import getLogger

from dotenv import load_dotenv

from . import __VERSION__ as APP_VERSION
from .app_config import load_app_config_from_env
from .subcommand.subcommand_update import (
    add_arguments_subcommand_update,
    execute_subcommand_update,
)

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
    subparser_update.set_defaults(handler=execute_subcommand_update)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()
