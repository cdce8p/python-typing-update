"""Comment is ignored"""
from __future__ import annotations

import sys
from typing import Any

var: Any = sys.version
var2: list[int]


def func(
    arg: int | str,  # comment
) -> list[int]:
    pass
