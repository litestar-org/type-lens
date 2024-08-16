from __future__ import annotations

import sys
import types
import typing
from typing import Any

from type_lens.type_view import TypeView

__all__ = [
    "get_type_hints",
]


def get_type_hints(
    obj: Any,
    globalns: dict[str, Any] | None = None,
    localns: dict[str, Any] | None = None,
    include_extras: bool = False,
) -> dict[str, Any]:
    """Provide a `get_type_hints` implementation that is consistent across python versions."""
    result: dict[str, Any] = _get_type_hints(obj, globalns=globalns, localns=localns, include_extras=include_extras)  # type: ignore[no-untyped-call]
    if sys.version_info < (3, 11):  # pragma: no cover
        result = fix_annotated_optional_type_hints(result)

    return result


def fix_annotated_optional_type_hints(
    hints: dict[str, typing.Any],
) -> dict[str, typing.Any]:  # pragma: no cover
    """Normalize `Annotated` interacting with `get_type_hints` in versions <3.11.

    https://github.com/python/cpython/issues/90353.
    """
    for param_name, hint in hints.items():
        type_view = TypeView(hint)
        if type_view.is_union and type_view.inner_types[0].is_annotated:
            hints[param_name] = type_view.inner_types[0].raw
    return hints


if sys.version_info >= (3, 10):
    _get_type_hints = typing.get_type_hints  # pyright: ignore

else:
    from eval_type_backport import eval_type_backport

    @typing.no_type_check
    def _get_type_hints(  # noqa: C901
        obj: typing.Any,
        globalns: dict[str, typing.Any] | None = None,
        localns: dict[str, typing.Any] | None = None,
        include_extras: bool = False,
    ) -> dict[str, typing.Any]:  # pragma: no cover
        """Backport from python 3.10.8, with exceptions.

        * Use `_forward_ref` instead of `typing.ForwardRef` to handle the `is_class` argument.
        * `eval_type_backport` instead of `eval_type`, to backport syntax changes in Python 3.10.

        https://github.com/python/cpython/blob/aaaf5174241496afca7ce4d4584570190ff972fe/Lib/typing.py#L1773-L1875
        """
        if getattr(obj, "__no_type_check__", None):
            return {}
        # Classes require a special treatment.
        if isinstance(obj, type):
            hints = {}
            for base in reversed(obj.__mro__):
                if globalns is None:
                    base_globals = getattr(sys.modules.get(base.__module__, None), "__dict__", {})
                else:
                    base_globals = globalns
                ann = base.__dict__.get("__annotations__", {})
                if isinstance(ann, types.GetSetDescriptorType):
                    ann = {}
                base_locals = dict(vars(base)) if localns is None else localns
                if localns is None and globalns is None:
                    # This is surprising, but required.  Before Python 3.10,
                    # get_type_hints only evaluated the globalns of
                    # a class.  To maintain backwards compatibility, we reverse
                    # the globalns and localns order so that eval() looks into
                    # *base_globals* first rather than *base_locals*.
                    # This only affects ForwardRefs.
                    base_globals, base_locals = base_locals, base_globals
                for name, value in ann.items():
                    if value is None:
                        value = type(None)
                    if isinstance(value, str):
                        value = _forward_ref(value, is_argument=False, is_class=True)

                    value = eval_type_backport(value, base_globals, base_locals)
                    hints[name] = value
            if not include_extras and hasattr(typing, "_strip_annotations"):
                return {k: typing._strip_annotations(t) for k, t in hints.items()}
            return hints

        if globalns is None:
            if isinstance(obj, types.ModuleType):
                globalns = obj.__dict__
            else:
                nsobj = obj
                # Find globalns for the unwrapped object.
                while hasattr(nsobj, "__wrapped__"):
                    nsobj = nsobj.__wrapped__
                globalns = getattr(nsobj, "__globals__", {})
            if localns is None:
                localns = globalns
        elif localns is None:
            localns = globalns
        hints = getattr(obj, "__annotations__", None)
        if hints is None:
            # Return empty annotations for something that _could_ have them.
            if isinstance(obj, typing._allowed_types):
                return {}

            raise TypeError(f"{obj!r} is not a module, class, method, " "or function.")
        defaults = typing._get_defaults(obj)
        hints = dict(hints)
        for name, value in hints.items():
            if value is None:
                value = type(None)
            if isinstance(value, str):
                # class-level forward refs were handled above, this must be either
                # a module-level annotation or a function argument annotation

                value = _forward_ref(
                    value,
                    is_argument=not isinstance(obj, types.ModuleType),
                    is_class=False,
                )
            value = eval_type_backport(value, globalns, localns)
            if name in defaults and defaults[name] is None:
                value = typing.Optional[value]
            hints[name] = value

        if not include_extras and hasattr(typing, "_strip_annotations"):
            return {k: typing._strip_annotations(t) for k, t in hints.items()}
        return hints


def _forward_ref(
    arg: typing.Any,
    is_argument: bool = True,
    *,
    is_class: bool = False,
) -> typing.ForwardRef:
    return typing.ForwardRef(arg, is_argument)
