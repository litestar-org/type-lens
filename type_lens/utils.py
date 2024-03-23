from __future__ import annotations

import typing as t
from collections import abc, defaultdict, deque

import typing_extensions as te

__all__ = (
    "get_instantiable_origin",
    "unwrap_annotation",
)


_WRAPPER_TYPES: te.Final = {te.Annotated, te.Required, te.NotRequired}
"""Types that always contain a wrapped type annotation as their first arg."""

_INSTANTIABLE_TYPE_MAPPING: te.Final = {
    abc.Mapping: dict,
    abc.MutableMapping: dict,
    abc.MutableSequence: list,
    abc.MutableSet: set,
    abc.Sequence: list,
    abc.Set: set,
    defaultdict: defaultdict,
    deque: deque,
    dict: dict,
    frozenset: frozenset,
    list: list,
    set: set,
    tuple: tuple,
}
"""A mapping of types to equivalent types that are safe to instantiate."""


def get_instantiable_origin(origin_type: t.Any, annotation: t.Any) -> t.Any:
    """Get a type that is safe to instantiate for the given origin type.

    If a builtin collection type is annotated without generic args, e.g, ``a: dict``, then the origin type will be
    ``None``. In this case, we can use the annotation to determine the correct instantiable type, if one exists.

    Args:
        origin_type: A type - would be the return value of :func:`get_origin()`.
        annotation: Type annotation associated with the origin type. Should be unwrapped from any wrapper types, such
            as ``Annotated``.

    Returns:
        A builtin type that is safe to instantiate for the given origin type.
    """
    if origin_type is None:
        return _INSTANTIABLE_TYPE_MAPPING.get(annotation)
    return _INSTANTIABLE_TYPE_MAPPING.get(origin_type, origin_type)


def unwrap_annotation(annotation: t.Any) -> tuple[t.Any, tuple[t.Any, ...], set[t.Any]]:
    """Remove "wrapper" annotation types, such as ``Annotated``, ``Required``, and ``NotRequired``.

    Note:
        ``annotation`` should have been retrieved from :func:`get_type_hints()` with ``include_extras=True``. This
        ensures that any nested ``Annotated`` types are flattened according to the PEP 593 specification.

    Args:
        annotation: A type annotation.

    Returns:
        A tuple of the unwrapped annotation and any ``Annotated`` metadata, and a set of any wrapper types encountered.
    """
    origin = te.get_origin(annotation)
    wrappers = set()
    metadata = []
    while origin in _WRAPPER_TYPES:
        wrappers.add(origin)
        annotation, *meta = te.get_args(annotation)
        metadata.extend(meta)
        origin = te.get_origin(annotation)
    return annotation, tuple(metadata), wrappers
