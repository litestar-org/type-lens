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
    """Represents a callable's signature, including all parameters and return type."""

    def __init__(self, fn: Callable[..., Any], type_hints: dict[str, type]) -> None:
        """Initialize CallableView.

        Args:
            fn: The callable to introspect.
            type_hints: Mapping of parameter names to types, as returned by ``get_type_hints()``.
                The ``"return"`` key, if present, is consumed as the return type annotation.
        """
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
        fn: Callable[..., Any],
        *,
        globalns: dict[str, Any] | None = None,
        localns: dict[str, Any] | None = None,
        include_extras: bool = False,
    ) -> Self:
        """Construct a :class:`CallableView` from a callable, resolving type hints automatically.

        Args:
            fn: The callable to introspect.
            globalns: Optional global namespace for resolving forward references.
            localns: Optional local namespace for resolving forward references.
            include_extras: Whether to preserve ``Annotated`` metadata in resolved type hints.

        Returns:
            A new :class:`CallableView` instance.
        """
        hint_fn = fn
        if not isinstance(fn, (type, types.FunctionType)):
            callable_ = getattr(fn, "__func__", None) or getattr(fn, "__call__", None)  # noqa: B004
            if not callable_:
                raise ValueError(f"{fn} is not a valid callable.")

            hint_fn = callable_

        result = get_type_hints(hint_fn, globalns=globalns, localns=localns, include_extras=include_extras)
        return cls(fn, result)
