# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

import argparse
import asyncio
import builtins
import logging
from functools import partial
from io import StringIO

import reorder_python_imports
from autoflake import _main as autoflake_main
from isort.main import main as isort_main
from pyupgrade._main import main as pyupgrade_main

from .utils import (
    async_check_uncommitted_changes, async_restore_files,
    check_comment_between_imports, check_files_exist)

logger = logging.getLogger("typing-update")


async def typing_update(
    loop: asyncio.AbstractEventLoop,
    filename: str,
    args: argparse.Namespace,
) -> tuple[int, str]:
    """Update typing syntax.

    Returns:
        - 0, filename: file was updated
        - 2, filename: if not typing update is necessary
    """
    null_file = StringIO()
    autoflake_partial = partial(autoflake_main, standard_out=null_file, standard_error=null_file)
    version_string = f"--py{''.join(map(str, args.min_version))}-plus"

    # Add, replace and reorder imports
    reorder_args: list[str | None] = []
    if args.min_version < (3, 10):
        reorder_args += ['--add-import', 'from __future__ import annotations']
    if args.full_reorder:
        if args.min_version >= (3, 9):
            reorder_args += [
                '--replace-import', 'typing=collections.abc:Hashable',
                '--replace-import', 'typing=collections.abc:Sized',
            ]
        reorder_args.append(version_string)
    reorder_args.append(filename)
    await loop.run_in_executor(
        None, reorder_python_imports.main,
        reorder_args,
    )

    # Run pyupgrade
    status_pyupgrade = await loop.run_in_executor(
        None, pyupgrade_main,
        [version_string, filename]
    )
    if status_pyupgrade == 0 and not args.full_reorder:
        # -> No updates made, revert changes
        return 2, filename

    # Check for unused imports (autoflake)
    try:
        await loop.run_in_executor(
            None, autoflake_partial,
            [None, '-c', filename],
        )
        if not args.full_reorder:
            # -> No unused imports, revert changes
            return 2, filename
    except SystemExit:
        pass

    # Remove unused imports (autoflake)
    try:
        await loop.run_in_executor(
            None, autoflake_partial,
            [None, '-i', filename],
        )
    except SystemExit:
        pass

    # Run isort
    try:
        await loop.run_in_executor(
            None, isort_main,
            [filename],
        )
    except SystemExit:
        pass

    # Run black
    if args.black:
        process = await asyncio.create_subprocess_shell(
            f"black {filename}",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.communicate()

    return 0, filename


async def async_run(args: argparse.Namespace) -> int:
    """Update Python typing syntax.

    Returns:
        0: Files updated or check passed
        1: Check did not pass, files would be updated
        2: Couldn't update all files
        10: At least one file doesn't exist
        11: Uncommited changes in '.py' files
        12: Debug mode
    """
    if file_errors := check_files_exist(args.filenames):
        print("Abort! Some filenames don't exist.")
        for file_ in file_errors:
            print(f" - {file_}")
        return 10

    if args.disable_committed_check is False \
            and await async_check_uncommitted_changes(args.filenames) is False:
        print("Abort! Commit all changes to '.py' files before running again.")
        return 11

    files_with_comments: list[str] = []
    for filename in args.filenames:
        with open(filename) as fp:
            if check_comment_between_imports(fp):
                files_with_comments.append(filename)
    files_with_comments = sorted(files_with_comments)

    loop = asyncio.get_running_loop()
    files_updated: list[str] = []
    files_no_changes: list[str] = []

    # Mock builtin print to omit output
    original_print = builtins.print
    builtins.print = lambda *args, **kwargs: None

    return_values = await asyncio.gather(
        *[typing_update(loop, filename, args) for filename in args.filenames])
    for status, filename in return_values:
        if status == 0:
            files_updated.append(filename)
        elif status == 2:
            files_no_changes.append(filename)

    builtins.print = original_print
    await async_restore_files(files_no_changes)

    if args.check is True:
        await async_restore_files(files_updated)
        if files_updated:
            print("The following files need to be updated:")
            for file_ in sorted(files_updated):
                print(f" - {file_}")
            return 1
        return 0

    if files_with_comments:
        if args.force:
            print("Force mode selected!")
            print("Make sure to double check:")
            for file_ in files_with_comments:
                print(f" - {file_}")
        else:
            print("Could not update all files, check:")
            for file_ in files_with_comments:
                print(f" - {file_}")
            await async_restore_files(files_with_comments)

    print("---")
    print(f"All files: {len(args.filenames)}")
    print(f"No changes: {len(files_no_changes)}")
    print(f"Files updated: {len(files_updated) - len(files_with_comments)}")
    print(f"Files (no automatic update): {len(files_with_comments)}")

    if not files_with_comments and not args.force and args.verbose == 0:
        return 0
    if files_with_comments:
        return 2
    if args.verbose > 0:
        return 12
    return 0
