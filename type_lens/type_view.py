from __future__ import annotations

from collections import abc
from collections.abc import Collection, Mapping
from typing import Annotated, Any, AnyStr, Final, ForwardRef, TypeVar, Union

from typing_extensions import NotRequired, Required, get_args, get_origin

from type_lens.types.builtins import UNION_TYPES, NoneType
from type_lens.utils import get_instantiable_origin, unwrap_annotation

__all__ = ("TypeView",)


class TypeView:
    """Represents a type annotation."""

    __slots__ = {
        "annotation": "The annotation with any 'wrapper' types removed, e.g. Annotated.",
        "args": "The result of calling get_args(annotation) after unwrapping Annotated, e.g. (int,).",
        "generic_origin": "An equivalent type to origin that can be safely used as a generic type across all supported Python versions.",
        "inner_types": "The type's generic args parsed as ParsedType, if applicable.",
        "instantiable_origin": "An equivalent type to origin that can be safely instantiated. E.g., Sequence -> list.",
        "is_annotated": "Whether the annotation included Annotated or not.",
        "is_not_required": "Whether the annotation included NotRequired or not.",
        "is_required": "Whether the annotation included Required or not.",
        "metadata": "Any metadata associated with the annotation via Annotated.",
        "origin": "The result of calling get_origin(annotation) after unwrapping Annotated, e.g. list.",
        "raw": "The annotation exactly as received.",
    }

    def __init__(self, annotation: Any) -> None:
        """Initialize ParsedType.

        Args:
            annotation: The type annotation. This should be extracted from the return of
                ``get_type_hints(..., include_extras=True)`` so that forward references are resolved and recursive
                ``Annotated`` types are flattened.

        Returns:
            ParsedType
        """
        unwrapped, metadata, wrappers = unwrap_annotation(annotation)
        origin = get_origin(unwrapped)

        args = () if origin is abc.Callable else get_args(unwrapped)

        self.raw: Final = annotation
        self.annotation: Final = unwrapped
        self.origin: Final = origin
        self.args: Final = args
        self.metadata: Final = metadata
        self.instantiable_origin: Final = get_instantiable_origin(origin, unwrapped)
        self.is_annotated: Final = Annotated in wrappers
        self.is_required: Final = Required in wrappers
        self.is_not_required: Final = NotRequired in wrappers
        self.inner_types: Final = tuple(TypeView(arg) for arg in args)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeView):
            return False

        if self.origin:
            return bool(self.origin == other.origin and self.inner_types == other.inner_types)

        return bool(self.annotation == other.annotation)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        raw = self.raw
        if isinstance(self.raw, type):
            raw = raw.__name__
        return f"{cls_name}({raw})"

    @property
    def is_forward_ref(self) -> bool:
        """Whether the annotation is a forward reference or not."""
        return isinstance(self.annotation, (str, ForwardRef))

    @property
    def is_mapping(self) -> bool:
        """Whether the annotation is a mapping or not."""
        return self.is_subclass_of(Mapping)

    @property
    def is_tuple(self) -> bool:
        """Whether the annotation is a ``tuple`` or not."""
        return self.is_subclass_of(tuple)

    @property
    def is_variadic_tuple(self) -> bool:
        """Whether the annotation is a ``tuple`` **and** is of unbounded length.

        Tuples like `tuple[int, ...]` represent a list-like unbounded sequence
        of a single type T.
        """
        return self.is_tuple and len(self.args) == 2 and self.args[1] == ...

    @property
    def is_type_var(self) -> bool:
        """Whether the annotation is a TypeVar or not."""
        return isinstance(self.annotation, TypeVar)

    @property
    def is_union(self) -> bool:
        """Whether the annotation is a union type or not."""
        return self.origin in UNION_TYPES

    @property
    def is_optional(self) -> bool:
        """Whether the annotation is Optional or not."""
        return bool(self.is_union and NoneType in self.args)

    @property
    def is_collection(self) -> bool:
        """Whether the annotation is a collection type or not."""
        return self.is_subclass_of(Collection)

    @property
    def is_non_string_collection(self) -> bool:
        """Whether the annotation is a non-string collection type or not."""
        return self.is_collection and not self.is_subclass_of((str, bytes))

    def is_subclass_of(self, cl: type[Any] | tuple[type[Any], ...]) -> bool:
        """Whether the annotation is a subclass of the given type.

        Where ``self.annotation`` is a union type, this method will return ``True`` when all members of the union are
        a subtype of ``cl``, otherwise, ``False``.

        Args:
            cl: The type to check, or tuple of types. Passed as 2nd argument to ``issubclass()``.

        Returns:
            Whether the annotation is a subtype of the given type(s).
        """
        if self.origin:
            if self.origin in UNION_TYPES:
                return all(t.is_subclass_of(cl) for t in self.inner_types)

            return self.origin not in UNION_TYPES and issubclass(self.origin, cl)

        if self.annotation is AnyStr:
            return issubclass(str, cl) or issubclass(bytes, cl)
        return self.annotation is not Any and not self.is_type_var and issubclass(self.annotation, cl)

    def has_inner_subclass_of(self, cl: type[Any] | tuple[type[Any], ...]) -> bool:
        """Whether any generic args are a subclass of the given type.

        Args:
            cl: The type to check, or tuple of types. Passed as 2nd argument to ``issubclass()``.

        Returns:
            Whether any of the type's generic args are a subclass of the given type.
        """
        return any(t.is_subclass_of(cl) for t in self.inner_types)

    def strip_optional(self) -> TypeView:
        if not self.is_optional:
            return self

        if len(self.args) == 2:
            return self.inner_types[0]

        args = tuple(a for a in self.args if a is not NoneType)
        non_optional = Union[args]
        return TypeView(non_optional)
