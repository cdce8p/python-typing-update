"""Comment will be kept"""
import sys
from typing import Any, List, Union

from my_package.const import Variable  # comment

var: Any = sys.version
var2: List[int]


def func(arg: Union[int, str]) -> List[int]:
    pass
