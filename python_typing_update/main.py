# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

import argparse
import asyncio
import builtins
import io
import logging
from collections.abc import Iterable
from functools import partial
from io import StringIO

import aiofiles
import reorder_python_imports
from autoflake import _main as autoflake_main
from isort.main import main as isort_main
from pyupgrade._main import main as pyupgrade_main

from .const import FileAttributes, FileStatus
from .utils import (
    async_check_uncommitted_changes, async_restore_files,
    check_comment_between_imports, check_files_exist, extract_imports)

logger = logging.getLogger("typing-update")


async def typing_update(
    loop: asyncio.AbstractEventLoop,
    filename: str,
    args: argparse.Namespace,
    file_status: FileStatus,
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
        if (
            args.keep_updates is False
            and args.full_reorder is False
            and FileStatus.COMMENT_TYPING not in file_status
        ):
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


async def async_load_files(
    args: argparse.Namespace,
    filenames: Iterable[str], *,
    check_comments: bool,
) -> dict[str, FileAttributes]:
    """Process files from file list."""
    active_tasks: int = 0

    async def async_load_file(filename: str) -> tuple[str, FileAttributes]:
        """Load file into memory and perform token analysis."""
        nonlocal active_tasks
        while active_tasks > args.concurrent_files:
            await asyncio.sleep(0)
        active_tasks += 1
        async with aiofiles.open(filename, encoding="utf-8") as fp:
            data = await fp.read()
        file_status = check_comment_between_imports(io.StringIO(data)) \
            if check_comments is True else FileStatus.CLEAR
        imports_set = extract_imports(io.StringIO(data))
        active_tasks -= 1
        return filename, FileAttributes(file_status, imports_set)

    results = await asyncio.gather(*[async_load_file(file_) for file_ in filenames])
    return dict(results)


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

    filenames: dict[str, FileAttributes] = await async_load_files(args, args.filenames, check_comments=True)

    if args.only_force:
        filenames = {filename: attrs for filename, attrs in filenames.items()
                     if attrs.status != FileStatus.CLEAR}

    loop = asyncio.get_running_loop()
    files_updated: list[str] = []
    files_no_changes: list[str] = []

    # Mock builtin print to omit output
    original_print = builtins.print
    builtins.print = lambda *args, **kwargs: None

    return_values = await asyncio.gather(
        *[typing_update(loop, filename, args, attrs.status) for filename, attrs in filenames.items()])
    for status, filename in return_values:
        if status == 0:
            files_updated.append(filename)
        elif status == 2:
            files_no_changes.append(filename)

    builtins.print = original_print
    await async_restore_files(files_no_changes)

    if args.limit > 0 and len(files_updated) > args.limit:
        print(
            f"Limit applied! Only updated the first {args.limit} "
            f"of {len(files_updated)} files")
        async_restore_files(files_updated[args.limit:])
        files_updated = files_updated[:args.limit]

    if args.check is True:
        await async_restore_files(files_updated)
        if files_updated:
            print("The following files need to be updated:")
            for file_ in sorted(files_updated):
                print(f" - {file_}")
            return 1
        return 0

    files_updated_set: set[str] = set(files_updated)
    files_with_comments = sorted([
        filename for filename, attrs in filenames.items()
        if FileStatus.COMMENT in attrs.status and filename in files_updated_set
    ])
    files_imports_changed: list[str] = []
    for file_, attrs in (await async_load_files(args, files_updated_set, check_comments=False)).items():
        import_diff = filenames[file_].imports.difference(attrs.imports)
        for import_ in import_diff:
            if not import_.startswith('typing'):
                files_imports_changed.append(file_)
                break
    files_imports_changed = sorted(files_imports_changed)
    files_no_automatic_update = set(files_with_comments + files_imports_changed)

    if files_no_automatic_update:
        if args.force or args.only_force:
            print("Force mode selected!")
            print("Make sure to double check:")
            for file_ in files_with_comments:
                print(f" - {file_}")
            if files_with_comments and files_imports_changed:
                print(" --")
            for file_ in files_imports_changed:
                print(f" - {file_}")
        else:
            print("Could not update all files, check:")
            for file_ in files_with_comments:
                print(f" - {file_}")
            if files_with_comments and files_imports_changed:
                print(" --")
            for file_ in files_imports_changed:
                print(f" - {file_}")
            await async_restore_files(files_no_automatic_update)

    print("---")
    print(f"All files: {len(filenames)}")
    print(f"No changes: {len(files_no_changes)}")
    print(f"Files updated: {len(files_updated) - len(files_no_automatic_update)}")
    print(f"Files (no automatic update): {len(files_no_automatic_update)}")

    if (
        not files_no_automatic_update
        and not args.force
        and not args.only_force
        and args.verbose == 0
    ):
        return 0
    if files_no_automatic_update:
        return 2
    if args.verbose > 0:
        return 12
    return 0
