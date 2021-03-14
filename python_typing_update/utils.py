# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import os
from pathlib import Path


def check_files_exist(file_list: list[str]) -> list[str]:
    """Check if all files exist. Return False if not."""
    file_errors: list[str] = []
    cwd = Path(os.getcwd())
    for file_ in file_list:
        if cwd.joinpath(file_).is_file() is False:
            file_errors.append(file_)
    return sorted(file_errors)


async def async_restore_files(file_list: list[str]) -> None:
    if not file_list:
        return
    process = await asyncio.create_subprocess_shell(
        f"git restore -- {' '.join(file_list)}",
    )
    await process.communicate()


async def async_check_uncommitted_changes(file_list: list[str]) -> bool:
    """Check for uncommitted changes.

    Returns:
        False: if changes still need to be committed
    """
    process = await asyncio.create_subprocess_shell(
        "git diff-index --name-only HEAD --",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate()
    files_uncommitted: set[str] = {file_ for item in stdout.decode().split('\n')
                                   if (file_ := item.strip())}
    return not any(True for file_ in file_list if file_ in files_uncommitted)


async def async_check_changes(file_list: list[str]) -> list[str]:
    """Check if comment was change in files.

    That is a sing we can't update it automatically.
    """
    if not file_list:
        return []
    process = await asyncio.create_subprocess_shell(
        f"git diff -G\"^#|^from.*#|^import.*#\" --name-only -- {' '.join(file_list)}",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate()
    return sorted([file_ for file_ in stdout.decode().strip().split('\n') if file_])
