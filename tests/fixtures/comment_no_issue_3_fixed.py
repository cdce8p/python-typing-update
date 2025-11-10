"""Comment is ignored"""
import sys
from typing import Any

var: Any = sys.version
var2: list[int]


def func(
    arg: int | str,  # comment
) -> list[int]:
    pass
