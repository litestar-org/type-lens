from __future__ import annotations

import typing as t
from collections import abc, defaultdict, deque

import typing_extensions as te

from type_lens.types.builtins import UNION_TYPES

__all__ = ("unwrap_annotation", "SAFE_GENERIC_ORIGIN_MAP", "INSTANTIABLE_TYPE_MAPPING")

SAFE_GENERIC_ORIGIN_MAP: te.Final[dict[object, object]] = {
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

_WRAPPER_TYPES: te.Final = {te.Annotated, te.Required, te.NotRequired}
"""Types that always contain a wrapped type annotation as their first arg."""

INSTANTIABLE_TYPE_MAPPING: te.Final = {
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
