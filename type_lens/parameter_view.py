from __future__ import annotations

from inspect import Signature
from typing import TYPE_CHECKING, Final

from type_lens.exc import ParameterViewError
from type_lens.type_view import TypeView
from type_lens.types.empty import Empty, EmptyType

__all__ = ("ParameterView",)


if TYPE_CHECKING:
    from inspect import Parameter
    from typing import Any

    from typing_extensions import Self


class ParameterView:
    """Represents the parameters of a callable."""

    __slots__ = {
        "name": "The name of the parameter.",
        "default": "The default value of the parameter.",
        "type_view": "View of the parameter's annotation type.",
    }

    def __init__(self, name: str, type_view: TypeView, *, default: Any | EmptyType = Empty) -> None:
        self.name: Final = name
        self.type_view: Final = type_view
        self.default: Final = default

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
        try:
            annotation = fn_type_hints[parameter.name]
        except KeyError as err:
            msg = f"No annotation found for '{parameter.name}'"
            raise ParameterViewError(msg) from err

        return cls(
            name=parameter.name,
            default=Empty if parameter.default is Signature.empty else parameter.default,
            type_view=TypeView(annotation),
        )
