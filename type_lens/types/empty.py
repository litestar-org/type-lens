from __future__ import annotations

from typing_extensions import TypeAlias

__all__ = ("Empty", "EmptyType")

from enum import Enum
from typing import Final, Literal


class _EmptyEnum(Enum):
    """A sentinel enum used as placeholder."""

    EMPTY = 0


EmptyType: TypeAlias = Literal[_EmptyEnum.EMPTY]
Empty: Final = _EmptyEnum.EMPTY
