# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import os
import token
import tokenize
from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from .const import FileStatus


def check_files_exist(file_list: Iterable[str]) -> list[str]:
    """Check if all files exist. Return False if not."""
    file_errors: list[str] = []
    cwd = Path(os.getcwd())
    for file_ in file_list:
        if cwd.joinpath(file_).is_file() is False:
            file_errors.append(file_)
    return sorted(file_errors)


async def async_restore_files(file_list: Iterable[str]) -> None:
    if not file_list:
        return
    process = await asyncio.create_subprocess_shell(
        f"git restore -- {' '.join(file_list)}",
    )
    await process.communicate()


async def async_check_uncommitted_changes(file_list: Iterable[str]) -> bool:
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


def check_comment_between_imports(fp: TextIO) -> FileStatus:
    """Return True if comment is found between imports.

    Sign that the file can't be updated automatically.
    """
    flag_in_import_block: bool = False
    flag_multiple_imports: bool = False
    flag_typing_import: bool = False
    token_name_count: int = 0
    line_first_import: int | None = None
    line_last_import: int = 0
    line_comments: list[tuple[int, int]] = []
    return_value: FileStatus = FileStatus.CLEAR

    tokens = tokenize.generate_tokens(fp.readline)
    while True:
        try:
            t = next(tokens)
            if flag_in_import_block is True:
                if t.type == token.NAME and token_name_count == 0:
                    token_name_count += 1
                    if t.string == 'typing':
                        flag_typing_import = True
                elif t.type == token.NEWLINE:
                    flag_in_import_block = False
                    flag_multiple_imports = False
                    flag_typing_import = False
                    token_name_count = 0
                elif t.type == token.OP and t.string != '.':
                    flag_multiple_imports = True
                elif t.type == token.COMMENT:
                    if flag_typing_import is True:
                        return_value = return_value | FileStatus.COMMENT | FileStatus.COMMENT_TYPING
                    elif flag_multiple_imports is True:
                        # Comment in same line as import statement
                        return_value = return_value | FileStatus.COMMENT
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

    if return_value != FileStatus.CLEAR:
        # If inline comment was detected, stop here
        return return_value

    for _, line_number in line_comments:
        if line_first_import is None:
            # No import block detected
            return FileStatus.CLEAR
        if (line_first_import < line_number < line_last_import):
            # Report all comments in the main import block
            return FileStatus.COMMENT
    return FileStatus.CLEAR


def extract_imports(fp: TextIO) -> set[str]:
    """Create set of all imports in main import block."""
    flag_in_import_block: bool = False
    flag_relative_import: bool | None = None
    flag_imports: bool = False
    flag_last_token_name: bool = False
    current_package: str = ''
    imports: set[str] = set()

    tokens = tokenize.generate_tokens(fp.readline)
    while True:
        try:
            t = next(tokens)
            if flag_in_import_block is True:
                if t.type == token.NEWLINE:
                    if flag_relative_import is False:
                        imports.add(current_package)
                    flag_in_import_block = False
                    flag_relative_import = None
                    flag_imports = False
                    flag_last_token_name = False
                    current_package = ''
                elif t.type == token.NAME and t.string == 'import':
                    flag_imports = True
                elif t.type == token.NAME and flag_last_token_name is False:
                    if (
                        flag_relative_import is False
                        or flag_relative_import is True
                        and flag_imports is False
                    ):
                        current_package += t.string
                    elif flag_relative_import is True and flag_imports is True:
                        imports.add(f"{current_package}.{t.string}")
                elif t.type == token.OP and t.string == '.':
                    current_package += '.'
                elif t.type == token.OP and t.string == ',' and flag_relative_import is False:
                    imports.add(current_package)
                    current_package = ''

                flag_last_token_name = (t.type == token.NAME and t.string != 'import')
                continue
            if t.type == token.NAME:
                if t.string == 'import':
                    flag_in_import_block = True
                    flag_relative_import = False
                elif t.string == 'from':
                    flag_in_import_block = True
                    flag_relative_import = True
                else:
                    break
        except StopIteration:
            break
    return imports
