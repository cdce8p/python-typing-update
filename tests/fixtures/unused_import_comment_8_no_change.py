"""Test unused import retention."""
from logging import (  # unused-import
    DEBUG, INFO,
    WARNING)
from typing import Any, List

var1: List[str]
var2: Any
