from __future__ import annotations

import typing as t
from collections import abc, defaultdict, deque

import typing_extensions as te

from type_lens.types import UNION_TYPES

__all__ = (
    "get_generic_origin",
    "get_instantiable_origin",
    "unwrap_annotation",
)


_WRAPPER_TYPES: te.Final = {te.Annotated, te.Required, te.NotRequired}
"""Types that always contain a wrapped type annotation as their first arg."""

_GENERIC_ORIGIN_MAP: te.Final[dict[t.Any, t.Any]] = {
    set: t.AbstractSet,
    defaultdict: t.DefaultDict,
    deque: t.Deque,
    dict: t.Dict,
    frozenset: t.FrozenSet,
    list: t.List,
    tuple: t.Tuple,
    abc.Mapping: t.Mapping,
    abc.MutableMapping: t.MutableMapping,
    abc.MutableSequence: t.MutableSequence,
    abc.MutableSet: t.MutableSet,
    abc.Sequence: t.Sequence,
    abc.Set: t.AbstractSet,
    abc.Collection: t.Collection,
    abc.Container: t.Container,
    abc.ItemsView: t.ItemsView,
    abc.KeysView: t.KeysView,
    abc.MappingView: t.MappingView,
    abc.ValuesView: t.ValuesView,
    abc.Iterable: t.Iterable,
    abc.Iterator: t.Iterator,
    abc.Generator: t.Generator,
    abc.Reversible: t.Reversible,
    abc.Coroutine: t.Coroutine,
    abc.AsyncGenerator: t.AsyncGenerator,
    abc.AsyncIterable: t.AsyncIterable,
    abc.AsyncIterator: t.AsyncIterator,
    abc.Awaitable: t.Awaitable,
    **{union_t: t.Union for union_t in UNION_TYPES},
}
"""A mapping of types to equivalent types that are safe to be used as generics across all Python versions.

This is necessary because occasionally we want to rebuild a generic outer type with different args, and types such as
``collections.abc.Mapping``, are not valid generic types in Python 3.8.
"""

_INSTANTIABLE_TYPE_MAPPING: te.Final = {
    t.AbstractSet: set,
    t.DefaultDict: defaultdict,
    t.Deque: deque,
    t.Dict: dict,
    t.FrozenSet: frozenset,
    t.List: list,
    t.Mapping: dict,
    t.MutableMapping: dict,
    t.MutableSequence: list,
    t.MutableSet: set,
    t.Sequence: list,
    t.Set: set,
    t.Tuple: tuple,
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


def get_generic_origin(origin_type: t.Any, annotation: t.Any) -> t.Any:
    """Get a type that is safe to use as a generic type across all supported Python versions.

    If a builtin collection type is annotated without generic args, e.g, ``a: dict``, then the origin type will be
    ``None``. In this case, we can use the annotation to determine the correct generic type, if one exists.

    Args:
        origin_type: A type - would be the return value of :func:`get_origin()`.
        annotation: Type annotation associated with the origin type. Should be unwrapped from any wrapper types, such
            as ``Annotated``.

    Returns:
        The ``typing`` module equivalent of the given type, if it exists. Otherwise, the original type is returned.
    """
    if origin_type is None:
        return _GENERIC_ORIGIN_MAP.get(annotation)
    return _GENERIC_ORIGIN_MAP.get(origin_type, origin_type)


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
