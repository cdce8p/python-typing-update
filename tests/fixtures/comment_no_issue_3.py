"""Comment is ignored"""
import sys
from typing import Any, List, Union

var: Any = sys.version
var2: List[int]


def func(
    arg: Union[int, str],  # comment
) -> List[int]:
    pass
