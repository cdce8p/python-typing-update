"""Comment is ignored"""
from __future__ import annotations

import sys
from typing import Any

var: Any = sys.version
var2: list[int]  # comment


def func(
    arg: int | str,
) -> list[int]:
    pass
