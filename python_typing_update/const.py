# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from __future__ import annotations

from enum import Flag, auto
from typing import NamedTuple


class FileAttributes(NamedTuple):
    status: FileStatus
    imports: set[str]


class FileStatus(Flag):
    CLEAR = 0
    COMMENT = auto()
    COMMENT_TYPING = auto()
