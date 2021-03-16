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


async def async_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tool to update Python typing syntax.",
    )
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
        '--concurrent-files', type=int, default=100,
        help="Number of files to process concurrently during initial load. (default: %(default)s)"
    )
    parser.add_argument(
        '--full-reorder',
        action='store_true',
        help="Add version_str to 'reorder-python-import' args",
    )
    parser.add_argument(
        '--black',
        action='store_true',
        help="Run black formatting after update",
    )
    parser.add_argument(
        '--disable-committed-check',
        action='store_true', help=argparse.SUPPRESS,
        # Don't abort with uncommited changes
        # Use for testing only!
    )

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
        '--check',
        action='store_true',
        help="Check if files would be updated",
    )
    group1.add_argument(
        '--force',
        action='store_true',
        help="Update all files. Double check changes afterwards!",
    )
    group1.add_argument(
        '--only-force',
        action='store_true',
        help="Only update files which are likely to require extra work",
    )

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument(
        '--py38-plus',
        action='store_const', dest='min_version', default=(3, 8), const=(3, 8),
    )
    group2.add_argument(
        '--py39-plus',
        action='store_const', dest='min_version', const=(3, 9),
    )
    group2.add_argument(
        '--py310-plus',
        action='store_const', dest='min_version', const=(3, 10),
    )

    argv = argv or sys.argv[1:]
    args = parser.parse_args(argv)

    logging.basicConfig()
    if args.verbose > 0:
        logger.setLevel(logging.DEBUG)

    return await async_run(args)


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(async_main(argv))


if __name__ == '__main__':
    sys.exit(main())
