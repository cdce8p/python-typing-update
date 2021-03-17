"""Comment will be changed. Only valid with '--force'."""
import sys
from typing import (  # this comment should not be deleted
    Any, List, Union)

var: Any = sys.version
var2: List[int]


def func(
    arg: Union[int, str],
) -> List[int]:
    pass
