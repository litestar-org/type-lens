from __future__ import annotations

from collections import abc
from collections.abc import Collection, Mapping
from typing import Any, AnyStr, Final, ForwardRef, Generic, Literal, TypeVar, Union

from typing_extensions import Annotated, NotRequired, Required, get_args, get_origin

from type_lens.types.builtins import UNION_TYPES, NoneType
from type_lens.utils import get_instantiable_origin, get_safe_generic_origin, unwrap_annotation

__all__ = ("TypeView",)


T = TypeVar("T")


class TypeView(Generic[T]):
    """Represents a type annotation."""

    __slots__ = {
        "annotation": "The annotation with any 'wrapper' types removed, e.g. Annotated.",
        "args": "The result of calling get_args(annotation) after unwrapping Annotated, e.g. (int,).",
        "inner_types": "The type's generic args parsed as ParsedType, if applicable.",
        "metadata": "Any metadata associated with the annotation via Annotated.",
        "origin": "The result of calling get_origin(annotation) after unwrapping Annotated, e.g. list.",
        "raw": "The annotation exactly as received.",
        "_wrappers": "A set of wrapper types that were removed from the annotation.",
    }

    def __init__(self, annotation: T) -> None:
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

        self.raw: Final[T] = annotation
        self.annotation: Final = unwrapped
        self.origin: Final = origin
        self.args: Final = args
        self.metadata: Final = metadata
        self._wrappers: Final = wrappers
        self.inner_types: Final = tuple(TypeView(arg) for arg in args)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeView):
            return False

        if self.origin:
            return bool(self.origin == other.origin and self.inner_types == other.inner_types)

        return bool(self.annotation == other.annotation)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.repr_type})"

    @property
    def repr_type(self) -> str:
        if isinstance(self.annotation, type) or self.origin:
            if self.is_literal:
                name = "Literal"
            elif self.is_union:
                name = "Union"
            else:
                name = self.annotation.__name__
        else:
            name = repr(self.annotation)

        if self.origin:
            inner_types = ", ".join(t.repr_type for t in self.inner_types)
            name = f"{name}[{inner_types}]"

        return str(name)

    @property
    def allows_none(self) -> bool:
        """Whether the annotation supports being assigned ``None``."""
        return self.is_optional or self.is_none_type

    @property
    def instantiable_origin(self) -> Any:
        """An instantiable type that is consistent with the origin type of the annotation.

        Examples:
            >>> from type_lens import TypeView
            >>> from collections.abc import Sequence
            >>> TypeView(Sequence[int]).instantiable_origin
            <class 'list'>

        Returns:
            An instantiable type that is consistent with the origin type of the annotation.
        """
        return get_instantiable_origin(self)

    @property
    def is_annotated(self) -> bool:
        """Whether the annotation was wrapped in Annotated or not.

        This would indicate that the annotation has metadata associated with it.
        """
        return Annotated in self._wrappers

    @property
    def is_collection(self) -> bool:
        """Whether the annotation is a collection type or not."""
        return self.is_subtype_of(Collection)

    @property
    def is_forward_ref(self) -> bool:
        """Whether the annotation is a forward reference or not."""
        return isinstance(self.annotation, (str, ForwardRef))

    @property
    def is_literal(self) -> bool:
        """Whether the annotation is a literal value or not."""
        return self.origin is Literal

    @property
    def is_mapping(self) -> bool:
        """Whether the annotation is a mapping or not."""
        return self.is_subtype_of(Mapping)

    @property
    def is_non_string_collection(self) -> bool:
        """Whether the annotation is a non-string collection type or not."""
        return self.is_collection and not self.is_subtype_of((str, bytes))

    @property
    def is_none_type(self) -> bool:
        """Whether the annotation is NoneType or not."""
        return self.annotation in {None, NoneType}

    @property
    def is_not_required(self) -> bool:
        """Whether the annotation was wrapped in NotRequired or not."""
        return NotRequired in self._wrappers

    @property
    def is_optional(self) -> bool:
        """Whether the annotation is Optional or not."""
        return bool(self.is_union and NoneType in self.args)

    @property
    def is_required(self) -> bool:
        """Whether the annotation was wrapped in Required or not."""
        return Required in self._wrappers

    @property
    def is_tuple(self) -> bool:
        """Whether the annotation is a ``tuple`` or not."""
        return self.is_subtype_of(tuple)

    @property
    def is_type_var(self) -> bool:
        """Whether the annotation is a TypeVar or not."""
        return isinstance(self.annotation, TypeVar)

    @property
    def is_union(self) -> bool:
        """Whether the annotation is a union type or not."""
        return self.origin in UNION_TYPES

    @property
    def is_variadic_tuple(self) -> bool:
        """Whether the annotation is a ``tuple`` **and** is of unbounded length.

        Tuples like `tuple[int, ...]` represent a list-like unbounded sequence
        of a single type T.
        """
        return self.is_tuple and len(self.args) == 2 and self.args[1] == ...

    @property
    def safe_generic_origin(self) -> Any:
        """An object safe to be used as a generic type across all supported Python versions.

        Examples:
            >>> from type_lens import TypeView
            >>> TypeView(dict[str, int]).safe_generic_origin
            typing.Dict
        """
        return get_safe_generic_origin(self)

    def has_inner_subtype_of(self, typ: type[Any] | tuple[type[Any], ...]) -> bool:
        """Whether any generic args are a subclass of the given type.

        Args:
            typ: The type to check, or tuple of types. Passed as 2nd argument to ``issubclass()``.

        Returns:
            Whether any of the type's generic args are a subclass of the given type.
        """
        return any(t.is_subtype_of(typ) for t in self.inner_types)

    def is_subtype_of(self, typ: Any | tuple[Any, ...], /) -> bool:
        """Whether the annotation is a subtype of the given type.

        Where ``self.annotation`` is a union type, this method will return ``True`` when all members of the union are
        a subtype of ``cl``, otherwise, ``False``.

        Args:
            typ: The type to check, or tuple of types. Passed as 2nd argument to ``issubclass()``.

        Returns:
            Whether the annotation is a subtype of the given type(s).
        """
        if self.origin:
            if self.origin in UNION_TYPES:
                return all(t.is_subtype_of(typ) for t in self.inner_types)

            return self.origin not in UNION_TYPES and isinstance(self.origin, type) and issubclass(self.origin, typ)

        if self.annotation is AnyStr:
            return issubclass(str, typ) or issubclass(bytes, typ)
        return (
            self.annotation is not Any
            and not self.is_type_var
            and isinstance(self.annotation, type)
            and issubclass(self.annotation, typ)
        )

    def strip_optional(self) -> TypeView:
        if not self.is_optional:
            return self

        if len(self.args) == 2:
            return self.inner_types[0]

        args = tuple(a for a in self.args if a is not NoneType)
        non_optional = Union[args]  # type: ignore[valid-type]
        return TypeView(non_optional)
