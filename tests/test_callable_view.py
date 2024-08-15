from dataclasses import dataclass
from typing import Any, Optional, Union

import pytest
from typing_extensions import Annotated

from type_lens import CallableView, ParameterView, TypeView


def test_invalid() -> None:
    class Foo: ...

    instance = Foo()

    with pytest.raises(ValueError) as e:
        CallableView.from_callable(instance)  # type: ignore

    error = str(e.value)
    assert error.startswith("<tests.test_callable_view.test_invalid.<locals>.Foo object")
    assert error.endswith("is not a valid callable.")


def test_no_return_annotation() -> None:
    def fn():  # type: ignore[no-untyped-def]
        return

    function_view = CallableView.from_callable(fn)
    assert function_view.parameters == ()
    assert function_view.return_type == TypeView(None)


def test_return_annotation() -> None:
    def fn() -> int:
        return 4

    function_view = CallableView.from_callable(fn)
    assert function_view.parameters == ()
    assert function_view.return_type == TypeView(int)


def test_untyped_param() -> None:
    def fn(foo):  # type: ignore[no-untyped-def]
        return foo

    function_view = CallableView.from_callable(fn)
    assert function_view.parameters == (ParameterView("foo", TypeView(Any)),)


def test_typed_param() -> None:
    def fn(foo: int) -> int:
        return foo

    function_view = CallableView.from_callable(fn)
    assert function_view.parameters == (ParameterView("foo", TypeView(int)),)


def test_fix_annotated_optional_type_hints() -> None:
    def fn1(foo: Annotated[Optional[int], "d"] = None) -> Optional[int]:
        return foo

    def fn2(foo: Annotated[Optional[int], "d"] = None) -> Optional[int]:
        return foo

    fn_view1 = CallableView.from_callable(fn1, include_extras=True)
    assert fn_view1.parameters == (ParameterView("foo", TypeView(Annotated[Union[int, None], "d"]), default=None),)

    fn_view2 = CallableView.from_callable(fn2, include_extras=True)
    assert fn_view2.parameters == (ParameterView("foo", TypeView(Annotated[Union[int, None], "d"]), default=None),)


def test_class() -> None:
    @dataclass
    class Foo:
        a: int
        b: str = "asdf"

    fn_view1 = CallableView.from_callable(Foo, include_extras=True)
    assert fn_view1.parameters == (
        ParameterView("a", TypeView(int)),
        ParameterView("b", TypeView(str), default="asdf"),
    )


def test_class_instance() -> None:
    @dataclass
    class Foo:
        a: int
        b: str = "asdf"

        def __call__(self, c: bool) -> bool:
            return c

    foo = Foo(1, "qwer")

    fn_view1 = CallableView.from_callable(foo, include_extras=True)
    assert fn_view1.parameters == (ParameterView("c", TypeView(bool)),)
