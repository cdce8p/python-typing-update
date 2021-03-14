"""Comment is ignored"""
# This is a comment
import sys
from typing import Any, List, Union

var: Any = sys.version
var2: List[int]


def func(
    arg: Union[int, str],
) -> List[int]:
    pass
