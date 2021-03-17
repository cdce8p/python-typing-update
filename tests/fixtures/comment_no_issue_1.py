"""Comment is ignored"""
import sys
from typing import Any, List, Union

var: Any = sys.version
var2: List[int]

# This is a comment


def func(
    arg: Union[int, str],
) -> List[int]:
    pass
