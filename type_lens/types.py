from __future__ import annotations

import sys
from typing import Union

__all__ = ["UNION_TYPES", "NoneType"]

if sys.version_info >= (3, 10):
    from types import UnionType

    UNION_TYPES = {UnionType, Union}
else:  # pragma: no cover
    UNION_TYPES = {Union}

NoneType: type[None] = type(None)
