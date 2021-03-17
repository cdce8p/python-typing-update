"""Comment will be changed. Only valid with '--force'."""
from __future__ import annotations

import sys
from typing import Any

from xyz import not_exist

# This is a comment

var: Any = sys.version
var2: list[int]


def func(
    arg: int | str,
) -> list[int]:
    pass
