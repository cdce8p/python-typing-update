"""Comment is ignored"""
import sys
from typing import Any

var: Any = sys.version
var2: list[int]  # comment


def func(
    arg: int | str,
) -> list[int]:
    pass
