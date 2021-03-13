"""Update typing syntax for Python 3.8+"""
from __future__ import annotations

from collections.abc import Container, Hashable
from typing import Any

var1: list[str]
var2: Any
var3: int | str
var4: Hashable
var5: Container
