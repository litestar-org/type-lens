# ruff: noqa: UP006
from __future__ import annotations

import sys
from typing import (
    TYPE_CHECKING,
    Any,
    ForwardRef,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

import pytest
from typing_extensions import Annotated, NotRequired, Required, get_type_hints

from type_lens import TypeView
from type_lens.types.builtins import NoneType

if TYPE_CHECKING:
    from typing import Final


T = TypeVar("T")


def _check_parsed_type(type_lens: TypeView, expected: dict[str, Any]) -> None:
    __tracebackhide__ = True
    for key, expected_value in expected.items():
        lens_value = getattr(type_lens, key)
        if lens_value != expected_value:
            pytest.fail(f"Expected {key} to be {expected_value}, got {lens_value} instead. TypeLens: {type_lens}")


_type_lens_int: Final = TypeView(int)


class _TD(TypedDict):
    req_int: Required[int]
    req_list_int: Required[List[int]]
    not_req_int: NotRequired[int]
    not_req_list_int: NotRequired[List[int]]
    ann_req_int: Required[Annotated[int, "foo"]]
    ann_req_list_int: Required[Annotated[List[int], "foo"]]


_typed_dict_hints: Final = get_type_hints(_TD, include_extras=True)


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (
            int,
            {
                "raw": int,
                "annotation": int,
                "origin": None,
                "args": (),
                "metadata": (),
                "is_annotated": False,
                "is_required": False,
                "is_not_required": False,
                "inner_types": (),
            },
        ),
        (
            List[int],
            {
                "raw": List[int],
                "annotation": List[int],
                "origin": list,
                "args": (int,),
                "metadata": (),
                "is_annotated": False,
                "is_required": False,
                "is_not_required": False,
                "inner_types": (TypeView(int),),
            },
        ),
        (
            Annotated[int, "foo"],
            {
                "raw": Annotated[int, "foo"],
                "annotation": int,
                "origin": None,
                "args": (),
                "metadata": ("foo",),
                "is_annotated": True,
                "is_required": False,
                "inner_types": (),
            },
        ),
        (
            Annotated[List[int], "foo"],
            {
                "raw": Annotated[List[int], "foo"],
                "annotation": List[int],
                "origin": list,
                "args": (int,),
                "metadata": ("foo",),
                "is_annotated": True,
                "is_required": False,
                "is_not_required": False,
                "inner_types": (TypeView(int),),
            },
        ),
        (
            _typed_dict_hints["req_int"],
            {
                "raw": _typed_dict_hints["req_int"],
                "annotation": int,
                "origin": None,
                "args": (),
                "metadata": (),
                "is_annotated": False,
                "is_required": True,
                "is_not_required": False,
                "inner_types": (),
            },
        ),
        (
            _typed_dict_hints["req_list_int"],
            {
                "raw": _typed_dict_hints["req_list_int"],
                "annotation": List[int],
                "origin": list,
                "args": (int,),
                "metadata": (),
                "is_annotated": False,
                "is_required": True,
                "is_not_required": False,
                "inner_types": (TypeView(int),),
            },
        ),
        (
            _typed_dict_hints["not_req_int"],
            {
                "raw": _typed_dict_hints["not_req_int"],
                "annotation": int,
                "origin": None,
                "args": (),
                "metadata": (),
                "is_annotated": False,
                "is_required": False,
                "is_not_required": True,
                "inner_types": (),
            },
        ),
        (
            _typed_dict_hints["not_req_list_int"],
            {
                "raw": _typed_dict_hints["not_req_list_int"],
                "annotation": List[int],
                "origin": list,
                "args": (int,),
                "metadata": (),
                "is_annotated": False,
                "is_required": False,
                "is_not_required": True,
                "inner_types": (TypeView(int),),
            },
        ),
        (
            _typed_dict_hints["ann_req_int"],
            {
                "raw": _typed_dict_hints["ann_req_int"],
                "annotation": int,
                "origin": None,
                "args": (),
                "metadata": ("foo",),
                "is_annotated": True,
                "is_required": True,
                "is_not_required": False,
                "inner_types": (),
            },
        ),
        (
            _typed_dict_hints["ann_req_list_int"],
            {
                "raw": _typed_dict_hints["ann_req_list_int"],
                "annotation": List[int],
                "origin": list,
                "args": (int,),
                "metadata": ("foo",),
                "is_annotated": True,
                "is_required": True,
                "is_not_required": False,
                "inner_types": (TypeView(int),),
            },
        ),
    ],
)
def test_parsed_type_from_annotation(annotation: Any, expected: dict[str, Any]) -> None:
    """Test ParsedType.from_annotation."""
    _check_parsed_type(TypeView(annotation), expected)


def test_parsed_type_from_union_annotation() -> None:
    """Test ParsedType.from_annotation for Union."""
    annotation = Union[int, List[int]]
    expected = {
        "raw": annotation,
        "annotation": annotation,
        "origin": Union,
        "args": (int, List[int]),
        "metadata": (),
        "is_annotated": False,
        "is_required": False,
        "is_not_required": False,
        "inner_types": (TypeView(int), TypeView(List[int])),
    }
    _check_parsed_type(TypeView(annotation), expected)


@pytest.mark.parametrize("value", ["int", ForwardRef("int")])
def test_parsed_type_is_forward_ref_predicate(value: Any) -> None:
    """Test ParsedType with ForwardRef."""
    parsed_type = TypeView(value)
    assert parsed_type.is_forward_ref is True
    assert parsed_type.annotation == value
    assert parsed_type.origin is None
    assert parsed_type.args == ()
    assert parsed_type.metadata == ()
    assert parsed_type.is_annotated is False
    assert parsed_type.is_required is False
    assert parsed_type.is_not_required is False
    assert parsed_type.inner_types == ()


def test_parsed_type_is_type_var_predicate() -> None:
    """Test ParsedType.is_type_var."""
    assert TypeView(int).is_type_var is False
    assert TypeView(T).is_type_var is True
    assert TypeView(Union[int, T]).is_type_var is False  # pyright: ignore[reportGeneralTypeIssues]


def test_parsed_type_is_union_predicate() -> None:
    """Test ParsedType.is_union."""
    assert TypeView(int).is_union is False
    assert TypeView(Optional[int]).is_union is True
    assert TypeView(Union[int, None]).is_union is True
    assert TypeView(Union[int, str]).is_union is True


def test_parsed_type_is_optional_predicate() -> None:
    """Test ParsedType.is_optional."""
    assert TypeView(int).is_optional is False
    assert TypeView(Optional[int]).is_optional is True
    assert TypeView(Union[int, None]).is_optional is True
    assert TypeView(Union[int, None, str]).is_optional is True
    assert TypeView(Union[int, str]).is_optional is False


def test_parsed_type_is_subtype_of() -> None:
    """Test ParsedType.is_type_of."""
    assert TypeView(bool).is_subtype_of(int) is True
    assert TypeView(bool).is_subtype_of(str) is False
    assert TypeView(Union[int, str]).is_subtype_of(int) is False
    assert TypeView(List[int]).is_subtype_of(list) is True
    assert TypeView(List[int]).is_subtype_of(int) is False
    assert TypeView(Optional[int]).is_subtype_of(int) is False
    assert TypeView(Union[bool, int]).is_subtype_of(int) is True

    assert TypeView(None).is_subtype_of(int) is False
    assert TypeView(Literal[1]).is_subtype_of(int) is False


def test_parsed_type_has_inner_subtype_of() -> None:
    """Test ParsedType.has_type_of."""
    assert TypeView(List[int]).has_inner_subtype_of(int) is True
    assert TypeView(List[int]).has_inner_subtype_of(str) is False
    assert TypeView(List[Union[int, str]]).has_inner_subtype_of(int) is False


def test_parsed_type_equality() -> None:
    assert TypeView(int) == TypeView(int)
    assert TypeView(int) == TypeView(Annotated[int, "meta"])
    assert TypeView(int) != int
    assert TypeView(List[int]) == TypeView(List[int])
    assert TypeView(List[int]) != TypeView(List[str])
    assert TypeView(List[str]) != TypeView(Tuple[str])
    assert TypeView(Optional[str]) == TypeView(Union[str, None])


def test_tuple() -> None:
    assert TypeView(List[int]).is_tuple is False
    assert TypeView(List[int]).is_variadic_tuple is False

    assert TypeView(Tuple[int]).is_tuple is True
    assert TypeView(Tuple[int]).is_variadic_tuple is False

    assert TypeView(Tuple[int, int]).is_tuple is True
    assert TypeView(Tuple[int, int]).is_variadic_tuple is False

    assert TypeView(Tuple[int, ...]).is_tuple is True
    assert TypeView(Tuple[int, ...]).is_variadic_tuple is True


def test_strip_optional() -> None:
    # Non-optionals should return the original input
    assert TypeView(int).strip_optional() == TypeView(int)

    assert TypeView(Optional[int]).strip_optional() == TypeView(int)
    assert TypeView(Optional[Union[str, int]]).strip_optional() == TypeView(Union[str, int])
    assert TypeView(Union[str, int, None]).strip_optional() == TypeView(Union[str, int])


def test_repr() -> None:
    assert repr(TypeView(int)) == "TypeView(int)"
    assert repr(TypeView(Optional[str])) == "TypeView(Union[str, NoneType])"
    assert repr(TypeView(Literal["1", 2, True])) == "TypeView(Literal['1', 2, True])"


def test_is_none_type() -> None:
    assert TypeView(int).is_none_type is False
    assert TypeView(None).is_none_type is True
    assert TypeView(NoneType).is_none_type is True
    assert TypeView(Annotated[None, 4]).is_none_type is True
    assert TypeView(Union[int, None]).inner_types[1].is_none_type is True


def test_literal() -> None:
    assert TypeView(int).is_literal is False
    assert TypeView(Literal[4]).is_literal is True
    assert TypeView(4).is_literal is False


def test_allows_none() -> None:
    assert TypeView(int).allows_none is False
    assert TypeView(Optional[int]).allows_none is True
    assert TypeView(None).allows_none is True


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (int, None),
        (Optional[int], Union),
        (Union[int, None], Union),
        pytest.param(
            "int | str", Union, marks=pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10")
        ),
        pytest.param(
            "list[int]", List, marks=pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires Python 3.9")
        ),
    ],
)
def test_safe_generic_origin(annotation: Any, expected: Any) -> None:
    if isinstance(annotation, str):
        annotation = eval(annotation)
    assert TypeView(annotation).safe_generic_origin is expected


def test_repr_type() -> None:
    assert TypeView(int).repr_type == "int"
    assert TypeView(str).repr_type == "str"
    assert TypeView(Optional[int]).repr_type in ("Optional[int]", "Union[int, NoneType]", "Union[int, None]")
    assert TypeView(Literal[1, "two"]).repr_type == "Literal[1, 'two']"
    assert TypeView(Union[Literal[1, "two"], bool]).repr_type == "Union[Literal[1, 'two'], bool]"

    if sys.version_info >= (3, 9):
        assert TypeView(set[bool]).repr_type == "set[bool]"
