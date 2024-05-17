from __future__ import annotations

import inspect
import sys
from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import get_type_hints

from type_lens.parameter_view import ParameterView
from type_lens.type_view import TypeView

__all__ = ("FunctionView",)


if TYPE_CHECKING:
    from typing_extensions import Self


class FunctionView:
    def __init__(self, fn: Callable, type_hints: dict[str, type]):
        self.function = fn
        self.signature = getattr(fn, "__signature__", None) or inspect.signature(fn)

        self.return_type = TypeView(type_hints.pop("return", None))

        self.parameters = tuple(
            ParameterView.from_parameter(param, type_hints) for param in self.signature.parameters.values()
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionView):
            return False

        return bool(
            self.function == other.function
            and self.parameters == other.parameters
            and self.return_type == other.return_type
        )

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        return f"{cls_name}({self.function.__name__})"

    @classmethod
    def from_type_hints(cls: type[Self], fn: Callable, include_extras: bool = False) -> Self:
        result = get_type_hints(fn, include_extras=include_extras)
        if sys.version_info < (3, 11):  # pragma: no cover
            result = _fix_annotated_optional_type_hints(result)

        return cls(fn, result)


def _fix_annotated_optional_type_hints(
    hints: dict[str, Any],
) -> dict[str, Any]:  # pragma: no cover
    """Normalize `Annotated` interacting with `get_type_hints` in versions <3.11.

    https://github.com/python/cpython/issues/90353.
    """
    for param_name, hint in hints.items():
        type_view = TypeView(hint)
        if type_view.is_union and type_view.inner_types[0].is_annotated:
            hints[param_name] = type_view.inner_types[0].raw
    return hints
