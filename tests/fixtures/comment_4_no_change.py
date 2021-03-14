"""Comment will be changed. Only valid with '--force'."""
import sys
from typing import Any, List, Union

# This is a comment
from xyz import not_exist

var: Any = sys.version
var2: List[int]


def func(
    arg: Union[int, str],
) -> List[int]:
    pass
