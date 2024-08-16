from __future__ import annotations

import inspect
import types
from typing import TYPE_CHECKING, Any, Callable

from type_lens.parameter_view import ParameterView
from type_lens.type_view import TypeView
from type_lens.typing import get_type_hints

__all__ = ("CallableView",)


if TYPE_CHECKING:
    from typing_extensions import Self


class CallableView:
    def __init__(self, fn: Callable, type_hints: dict[str, type]):
        self.callable = fn
        self.signature = getattr(fn, "__signature__", None) or inspect.signature(fn)

        return_annotation = type_hints.pop("return", None)
        self.return_type = TypeView(return_annotation)

        self.parameters = tuple(
            ParameterView.from_parameter(param, type_hints) for param in self.signature.parameters.values()
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CallableView):
            return False

        return bool(
            self.callable == other.callable
            and self.parameters == other.parameters
            and self.return_type == other.return_type
        )

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        return f"{cls_name}({self.callable.__name__})"

    @classmethod
    def from_callable(
        cls: type[Self],
        fn: Callable,
        *,
        globalns: dict[str, Any] | None = None,
        localns: dict[str, Any] | None = None,
        include_extras: bool = False,
    ) -> Self:
        hint_fn = fn
        if not isinstance(fn, (type, types.FunctionType)):
            callable_ = getattr(fn, "__func__", None) or getattr(fn, "__call__", None)  # noqa: B004
            if not callable_:
                raise ValueError(f"{fn} is not a valid callable.")

            hint_fn = callable_

        result = get_type_hints(hint_fn, globalns=globalns, localns=localns, include_extras=include_extras)
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
