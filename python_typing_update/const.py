# ---------------------------------------------------------------------------
# Licensed under the MIT License. See LICENSE file for license information.
# ---------------------------------------------------------------------------
from enum import Flag, auto

version = (0, 2, 0)
dev_version = 1

version_str = '.'.join(map(str, version))
if dev_version is not None:
    version_str += f'-dev{dev_version}'


class FileStatus(Flag):
    CLEAR = 0
    COMMENT = auto()
    COMMENT_TYPING = auto()
