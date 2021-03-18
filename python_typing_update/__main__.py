# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from .main import async_run

logger = logging.getLogger(__name__)


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(
        self, prog: str, indent_increment: int = 2,
        max_help_position: int = 24, width: int | None = None,
    ) -> None:
        max_help_position = 40
        super().__init__(
            prog, indent_increment=indent_increment,
            max_help_position=max_help_position, width=width)


async def async_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tool to update Python typing syntax.",
        formatter_class=CustomHelpFormatter,
    )
    mode_options = parser.add_argument_group("select different mode")
    py_version_options = parser.add_argument_group("python version options")

    parser.add_argument(
        '-v', '--verbose',
        action='count', default=0,
        help="Print debug log",
    )
    parser.add_argument(
        'filenames',
        nargs='+',
    )
    parser.add_argument(
        '--limit', type=int, default=0,
        help="Max number of files that should be changed. No performance improvement!",
    )
    parser.add_argument(
        '--concurrent-files', metavar="NUM", type=int, default=100,
        help="Number of files to process concurrently during initial load. (default: %(default)s)"
    )
    parser.add_argument(
        '--full-reorder',
        action='store_true',
        help="Add version_str to 'reorder-python-import' args",
    )
    parser.add_argument(
        '--keep-updates',
        action='store_true',
        help="Keep updates even if no import was removed",
    )
    parser.add_argument(
        '--black',
        action='store_true',
        help="Run black formatting after update",
    )
    parser.add_argument(
        '--disable-committed-check',
        action='store_true',
        help="Don't abort with uncommited changes. Don't use it in production!",
    )

    group_mode = mode_options.add_mutually_exclusive_group()
    group_mode.add_argument(
        '--check',
        action='store_true',
        help="Check if files would be updated",
    )
    group_mode.add_argument(
        '--force',
        action='store_true',
        help="Update all files. Double check changes afterwards!",
    )
    group_mode.add_argument(
        '--only-force',
        action='store_true',
        help="Only update files which are likely to require extra work",
    )

    group_py_version = py_version_options.add_mutually_exclusive_group()
    group_py_version.add_argument(
        '--py38-plus',
        action='store_const', dest='min_version', default=(3, 8), const=(3, 8),
        help="Default"
    )
    group_py_version.add_argument(
        '--py39-plus',
        action='store_const', dest='min_version', const=(3, 9),
    )
    group_py_version.add_argument(
        '--py310-plus',
        action='store_const', dest='min_version', const=(3, 10),
    )

    argv = argv or sys.argv[1:]
    args = parser.parse_args(argv)

    logging.basicConfig()
    if args.verbose > 0:
        logger.setLevel(logging.DEBUG)

    if args.black:
        try:
            # pylint: disable=unused-import,import-outside-toplevel
            import black  # noqa: F401
        except ImportError:
            print("Error! Black is not installed")
            return 2

    return await async_run(args)


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(async_main(argv))


if __name__ == '__main__':
    sys.exit(main())
