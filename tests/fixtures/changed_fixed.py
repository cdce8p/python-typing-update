"""Update typing syntax for Python 3.8+"""
from __future__ import annotations

from typing import Any, Container, Hashable

from typing_extensions import TypedDict, TypeGuard

var1: list[str]
var2: Any
var3: int | str
var4: Hashable
var5: Container
var6: TypedDict
var7: TypeGuard[int]
