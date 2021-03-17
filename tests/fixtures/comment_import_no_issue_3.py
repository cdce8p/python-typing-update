"""Comment will be kept"""
import sys
from typing import Any, List, Union

from .const import Variable  # this comment should not be deleted

var: Any = sys.version
var2: List[int]


def func(arg: Union[int, str]) -> List[int]:
    pass
