"""Comment will be kept"""
from __future__ import annotations

import sys
from typing import Any

from my_package.const import Variable  # comment

var: Any = sys.version
var2: list[int]


def func(arg: int | str) -> list[int]:
    pass
