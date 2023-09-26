from __future__ import annotations

from dataclasses import dataclass
from inspect import Signature
from typing import TYPE_CHECKING

from type_lens.exc import ParameterViewError
from type_lens.type_view import TypeView
from type_lens.types import Empty

__all__ = ("ParameterView",)


if TYPE_CHECKING:
    from inspect import Parameter
    from typing import Any, Self


@dataclass(frozen=True)
class ParameterView:
    """Represents the parameters of a callable."""

    __slots__ = (
        "name",
        "default",
        "type_view",
    )

    name: str
    """The name of the parameter."""
    default: Any | Empty
    """The default value of the parameter."""
    type_view: TypeView
    """View of the parameter's annotation type."""

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
