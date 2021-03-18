"""Update typing syntax for Python 3.8+"""
from typing import Any, Container, Hashable, List, Union

from typing_extensions import TypeGuard, TypedDict

var1: List[str]
var2: Any
var3: Union[int, str]
var4: Hashable
var5: Container
var6: TypedDict
var7: TypeGuard[int]
