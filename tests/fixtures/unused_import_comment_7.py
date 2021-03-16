"""Test unused import retention."""
from logging import DEBUG, INFO, WARNING  # unused-import
from typing import Any, List

var1: List[str]
var2: Any
