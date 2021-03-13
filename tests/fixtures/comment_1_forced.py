"""Comment will be changed. Only valid with '--force'."""
from __future__ import annotations

import sys
from typing import Any

# This is a comment

var: Any = sys.version
var2: list[int]


def func(
    arg: int | str,
) -> list[int]:
    pass
