# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import os
import token
import tokenize
from pathlib import Path
from typing import TextIO


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


def check_comment_between_imports(fp: TextIO) -> bool:
    """Return True if comment is found between imports.

    Sign that the file can't be updated automatically.
    """
    flag_in_import_block: bool = False
    line_first_import: int | None = None
    line_last_import: int = 0
    line_comments: list[tuple[int, int]] = []

    tokens = tokenize.generate_tokens(fp.readline)
    while True:
        try:
            t = next(tokens)
            if flag_in_import_block is True:
                if t.type == token.NEWLINE:
                    flag_in_import_block = False
                elif t.type == token.COMMENT:
                    # Comment in same line as import statement
                    return True
                continue
            if t.type == token.NAME:
                if t.string in ('import', 'from'):
                    flag_in_import_block = True
                    if line_first_import is None:
                        line_first_import = t.start[0]
                    line_last_import = t.start[0]
                else:
                    # Any other code block,
                    # not in main import block anymore
                    break
            elif t.type in (token.COMMENT, token.STRING):
                line_comments.append((t.type, t.start[0]))
        except StopIteration:
            break

    for token_type, line_number in line_comments:
        if line_first_import is None:
            # No import block detected
            return False
        if (
            token_type == token.COMMENT
            and line_number <= line_last_import
        ):
            # Report all comments before and in the main import block
            return True
        if (
            token_type == token.STRING
            and line_first_import <= line_number <= line_last_import
        ):
            # Only report strings if they are inbetween imports
            # Ignore any ones at beginning of file
            return True
    return False
