"""Comment will be changed. Only valid with '--force'."""
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
