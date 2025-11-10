"""Comment is ignored"""
# This is a comment
import sys
from typing import Any

var: Any = sys.version
var2: list[int]


def func(
    arg: int | str,
) -> list[int]:
    pass
