from __future__ import annotations

from inspect import Signature
from typing import TYPE_CHECKING, Any, Final

from type_lens.type_view import TypeView
from type_lens.types.empty import Empty, EmptyType

__all__ = ("ParameterView",)

if TYPE_CHECKING:
    from inspect import Parameter

    from typing_extensions import Self

_any_type_view = TypeView(Any)


class ParameterView:
    """Represents the parameters of a callable."""

    __slots__ = {
        "name": "The name of the parameter.",
        "default": "The default value of the parameter.",
        "type_view": "View of the parameter's annotation type.",
    }

    def __init__(self, name: str, type_view: TypeView = _any_type_view, *, default: Any | EmptyType = Empty) -> None:
        self.name: Final = name
        self.type_view: Final = type_view
        self.default: Final = default

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParameterView):
            return False

        return bool(self.name == other.name and self.type_view == other.type_view and self.default == other.default)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        args = [
            repr(self.name),
            repr(self.type_view) if self.type_view else None,
            f"default={self.default}" if self.default is not Empty else None,
        ]
        args_str = ", ".join(a for a in args if a is not None)
        return f"{cls_name}({args_str})"

    @property
    def has_default(self) -> bool:
        """Whether the parameter has a default value or not."""
        return self.default is not Empty

    @classmethod
    def from_parameter(cls, parameter: Parameter, fn_type_hints: dict[str, Any]) -> Self:
        """Initialize ParsedSignatureParameter.

        Args:
            parameter: inspect.Parameter
            fn_type_hints: mapping of names to types. Should be result of ``get_type_hints()``, preferably via the
            :attr:``get_fn_type_hints() <.utils.signature_parsing.get_fn_type_hints>` helper.

        Returns:
            ParsedSignatureParameter.
        """
        annotation = fn_type_hints.get(parameter.name, Any)

        return cls(
            name=parameter.name,
            default=Empty if parameter.default is Signature.empty else parameter.default,
            type_view=TypeView(annotation),
        )
