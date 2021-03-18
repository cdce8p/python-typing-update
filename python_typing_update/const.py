# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

from enum import Flag, auto
from typing import NamedTuple

version = (0, 3, 0)
dev_version = None

version_str = '.'.join(map(str, version))
if dev_version is not None:
    version_str += f'-dev{dev_version}'


class FileAttributes(NamedTuple):
    status: FileStatus
    imports: set[str]


class FileStatus(Flag):
    CLEAR = 0
    COMMENT = auto()
    COMMENT_TYPING = auto()
