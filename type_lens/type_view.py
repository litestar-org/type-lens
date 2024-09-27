from __future__ import annotations

from collections import abc
from collections.abc import Collection, Mapping
from typing import Any, AnyStr, Final, ForwardRef, Generic, Literal, TypeVar, Union, _SpecialForm

from typing_extensions import Annotated, NotRequired, Required, get_args, get_origin
from typing_extensions import Literal as ExtensionsLiteral

from type_lens.types.builtins import UNION_TYPES, NoneType
from type_lens.utils import INSTANTIABLE_TYPE_MAPPING, SAFE_GENERIC_ORIGIN_MAP, unwrap_annotation

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
        "fallback_origin": "The unsubscripted version of a type, distinct from 'origin' in that for non-generics, this is the original type.",
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

        args: tuple[Any, ...] = () if origin is abc.Callable else get_args(unwrapped)

        self.raw: Final[T] = annotation
        self.annotation: Final = unwrapped
        self.origin: Final = origin
        self.fallback_origin: Final = origin or unwrapped
        self.args: Final[tuple[Any, ...]] = args
        self.metadata: Final = metadata
        self._wrappers: Final = wrappers
        self.inner_types: Final = tuple(TypeView(arg) for arg in args)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeView):
            return False

        if self.origin:
            self_origin = Union if self.is_union else self.origin
            other_origin = Union if other.is_union else other.origin
            return bool(self_origin == other_origin and self.inner_types == other.inner_types)

        return bool(self.annotation == other.annotation)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.repr_type})"

    @property
    def repr_type(self) -> str:
        """Returns a consistent, canonical repr of the contained annotation.

        Removes preceding `typing.` prefix for built-in typing constructs. Python's
        native repr for `typing` types is inconsistent across python versions!
        """
        # Literal/Union both appear to have no name on some versions of python.
        if self.is_literal:
            name = "Literal"
        elif self.is_union:
            name = "Union"
        elif isinstance(self.annotation, (type, _SpecialForm)) or self.origin:
            try:
                name = self.annotation.__name__  # pyright: ignore[reportAttributeAccessIssue]
            except AttributeError:
                # Certain _SpecialForm items have no __name__ python 3.8.
                name = self.annotation._name  # pyright: ignore[reportAttributeAccessIssue]
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
        return INSTANTIABLE_TYPE_MAPPING.get(self.fallback_origin, self.fallback_origin)

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
        return self.origin in {Literal, ExtensionsLiteral}

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
        return self.is_subclass_of(tuple)

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
        """A type, safe to be used as a generic type across all supported Python versions.

        Examples:
            >>> from type_lens import TypeView
            >>> TypeView(dict[str, int]).safe_generic_origin
            typing.Dict
        """
        return SAFE_GENERIC_ORIGIN_MAP.get(self.fallback_origin)

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
            if self.is_union:
                return all(t.is_subtype_of(typ) for t in self.inner_types)

            return self.is_subclass_of(typ)

        if self.annotation is AnyStr:
            return TypeView(Union[str, bytes]).is_subtype_of(typ)
        return self.annotation is not Any and not self.is_type_var and self.is_subclass_of(typ)

    def is_subclass_of(self, typ: Any | tuple[Any, ...], /) -> bool:
        """Whether the annotation is a subclass of the given type.

        Args:
            typ: The type to check, or tuple of types. Passed as 2nd argument to ``issubclass()``.

        Returns:
            Whether the annotation is a subclass of the given type(s).
        """
        return isinstance(self.fallback_origin, type) and issubclass(self.fallback_origin, typ)

    def strip_optional(self) -> TypeView:
        if not self.is_optional:
            return self

        if len(self.args) == 2:
            return self.inner_types[0]

        args = tuple(a for a in self.args if a is not NoneType)
        non_optional = Union[args]  # type: ignore[valid-type]
        return TypeView(non_optional)
