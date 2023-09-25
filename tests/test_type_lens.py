# ruff: noqa: UP006
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ForwardRef, List, Optional, Tuple, TypedDict, TypeVar, Union

import pytest
from typing_extensions import Annotated, NotRequired, Required, get_type_hints

from type_lens import TypeLens

if TYPE_CHECKING:
    from typing import Final


T = TypeVar("T")


def _check_parsed_type(type_lens: TypeLens, expected: dict[str, Any]) -> None:
    __tracebackhide__ = True
    for key, expected_value in expected.items():
        lens_value = getattr(type_lens, key)
        if lens_value != expected_value:
            pytest.fail(f"Expected {key} to be {expected_value}, got {lens_value} instead. TypeLens: {type_lens}")


_type_lens_int: Final = TypeLens(int)


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
                "generic_origin": None,
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
                "generic_origin": List,
                "inner_types": (TypeLens(int),),
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
                "is_not_required": False,
                "generic_origin": None,
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
                "generic_origin": List,
                "inner_types": (TypeLens(int),),
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
                "generic_origin": None,
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
                "generic_origin": List,
                "inner_types": (TypeLens(int),),
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
                "generic_origin": None,
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
                "generic_origin": List,
                "inner_types": (TypeLens(int),),
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
                "generic_origin": None,
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
                "generic_origin": List,
                "inner_types": (TypeLens(int),),
            },
        ),
    ],
)
def test_parsed_type_from_annotation(annotation: Any, expected: dict[str, Any]) -> None:
    """Test ParsedType.from_annotation."""
    _check_parsed_type(TypeLens(annotation), expected)


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
        "generic_origin": Union,
        "inner_types": (TypeLens(int), TypeLens(List[int])),
    }
    _check_parsed_type(TypeLens(annotation), expected)


@pytest.mark.parametrize("value", ["int", ForwardRef("int")])
def test_parsed_type_is_forward_ref_predicate(value: Any) -> None:
    """Test ParsedType with ForwardRef."""
    parsed_type = TypeLens(value)
    assert parsed_type.is_forward_ref is True
    assert parsed_type.annotation == value
    assert parsed_type.origin is None
    assert parsed_type.args == ()
    assert parsed_type.metadata == ()
    assert parsed_type.is_annotated is False
    assert parsed_type.is_required is False
    assert parsed_type.is_not_required is False
    assert parsed_type.generic_origin is None
    assert parsed_type.inner_types == ()


def test_parsed_type_is_type_var_predicate() -> None:
    """Test ParsedType.is_type_var."""
    assert TypeLens(int).is_type_var is False
    assert TypeLens(T).is_type_var is True
    assert TypeLens(Union[int, T]).is_type_var is False


def test_parsed_type_is_union_predicate() -> None:
    """Test ParsedType.is_union."""
    assert TypeLens(int).is_union is False
    assert TypeLens(Optional[int]).is_union is True
    assert TypeLens(Union[int, None]).is_union is True
    assert TypeLens(Union[int, str]).is_union is True


def test_parsed_type_is_optional_predicate() -> None:
    """Test ParsedType.is_optional."""
    assert TypeLens(int).is_optional is False
    assert TypeLens(Optional[int]).is_optional is True
    assert TypeLens(Union[int, None]).is_optional is True
    assert TypeLens(Union[int, None, str]).is_optional is True
    assert TypeLens(Union[int, str]).is_optional is False


def test_parsed_type_is_subclass_of() -> None:
    """Test ParsedType.is_type_of."""
    assert TypeLens(bool).is_subclass_of(int) is True
    assert TypeLens(bool).is_subclass_of(str) is False
    assert TypeLens(Union[int, str]).is_subclass_of(int) is False
    assert TypeLens(List[int]).is_subclass_of(list) is True
    assert TypeLens(List[int]).is_subclass_of(int) is False
    assert TypeLens(Optional[int]).is_subclass_of(int) is False
    assert TypeLens(Union[bool, int]).is_subclass_of(int) is True


def test_parsed_type_has_inner_subclass_of() -> None:
    """Test ParsedType.has_type_of."""
    assert TypeLens(List[int]).has_inner_subclass_of(int) is True
    assert TypeLens(List[int]).has_inner_subclass_of(str) is False
    assert TypeLens(List[Union[int, str]]).has_inner_subclass_of(int) is False


def test_parsed_type_equality() -> None:
    assert TypeLens(int) == TypeLens(int)
    assert TypeLens(int) == TypeLens(Annotated[int, "meta"])
    assert TypeLens(int) != int
    assert TypeLens(List[int]) == TypeLens(List[int])
    assert TypeLens(List[int]) != TypeLens(List[str])
    assert TypeLens(List[str]) != TypeLens(Tuple[str])
    assert TypeLens(Optional[str]) == TypeLens(Union[str, None])
