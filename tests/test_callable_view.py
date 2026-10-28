from __future__ import annotations

import functools
import inspect
import sys
from dataclasses import dataclass
from typing import Any, List, Optional, Type, Union, cast

import pytest
from typing_extensions import Annotated

from type_lens import CallableView, ParameterView, TypeView


def test_invalid() -> None:
    class Foo: ...

    # Avoid linting deficiencies across versions.
    instance = cast(Type[Foo], Foo())

    with pytest.raises(ValueError) as e:
        CallableView.from_callable(instance)

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
        return foo  # pyright: ignore

    function_view = CallableView.from_callable(fn)  # pyright: ignore
    assert function_view.parameters == (ParameterView("foo", TypeView(Any), has_annotation=False),)


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


def test_instance_method() -> None:
    class Foo:
        def method(self, c: bool) -> bool:
            return c

    foo = Foo()

    fn_view1 = CallableView.from_callable(foo.method, include_extras=True)
    assert fn_view1.parameters == (ParameterView("c", TypeView(bool)),)


@pytest.mark.parametrize(
    ("hint",),
    [
        (Optional[str],),
        (Union[str, None],),
        (Union[str, int, None],),
        (Optional[Union[str, int]],),
        pytest.param(
            Union[str, int], marks=pytest.mark.xfail(sys.version_info < (3, 11), reason="Weird optional coercion")
        ),
        pytest.param(str, marks=pytest.mark.xfail(sys.version_info < (3, 11), reason="Weird optional coercion")),
    ],
)
def test_parameters_with_none_default(hint: Any) -> None:
    def fn(plain: hint = None, annotated: Annotated[hint, ...] = None) -> None: ...  # pyright: ignore

    fn_view = CallableView.from_callable(fn, localns=locals(), include_extras=True)  # pyright: ignore
    plain_param, annotated_param = fn_view.parameters
    assert plain_param.type_view.annotation == annotated_param.type_view.annotation


def test_evaluated_runtime_type() -> None:
    @dataclass
    class Foo:
        a: list[int] | None = None

    fn_view1 = CallableView.from_callable(Foo, include_extras=True)

    if sys.version_info < (3, 10):
        assert fn_view1.parameters == (ParameterView("a", TypeView(Union[List[int], None]), default=None),)  # pyright: ignore
    else:
        assert fn_view1.parameters == (ParameterView("a", TypeView(Union[list[int], None]), default=None),)  # pyright: ignore


def test_callable_wrapper_with_wrapped() -> None:
    class Wrapper:
        def __init__(self, wrapped: Any) -> None:
            functools.update_wrapper(self, wrapped)

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self.__wrapped__(*args, **kwargs)

    def foo(a: int, b: int) -> int:
        return a + b

    wrapped_foo = Wrapper(foo)
    foo_view = CallableView.from_callable(foo)
    wrapped_foo_view = CallableView.from_callable(wrapped_foo)

    assert wrapped_foo_view.parameters == foo_view.parameters
    assert wrapped_foo_view.return_type == foo_view.return_type
    assert wrapped_foo_view.parameters == (
        ParameterView("a", TypeView(int)),
        ParameterView("b", TypeView(int)),
    )
    assert wrapped_foo_view.return_type == TypeView(int)


def test_plain_callable_wrapper_with_wrapped_attribute() -> None:
    class PlainWrapper:
        def __init__(self, wrapped: Any) -> None:
            self.__wrapped__ = wrapped

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self.__wrapped__(*args, **kwargs)

    def foo(a: int, b: str = "default") -> bool:
        return True

    wrapped_foo = PlainWrapper(foo)
    wrapped_foo_view = CallableView.from_callable(wrapped_foo)

    assert wrapped_foo_view.parameters == (
        ParameterView("a", TypeView(int)),
        ParameterView("b", TypeView(str), default="default"),
    )
    assert wrapped_foo_view.return_type == TypeView(bool)


def test_wrapper_with_signature_override() -> None:
    class IntWrapper:
        def __init__(self, wrapped: Any) -> None:
            functools.update_wrapper(self, wrapped)
            self.__signature__ = inspect.signature(wrapped).replace(
                return_annotation=int,
            )

        def __call__(self, *args: Any, **kwargs: Any) -> int:
            return int(self.__wrapped__(*args, **kwargs))

    def foo(a: int, b: int) -> int | str:
        return a + b

    wrapped_foo = IntWrapper(foo)
    wrapped_foo_view = CallableView.from_callable(wrapped_foo)

    assert wrapped_foo_view.parameters == (
        ParameterView("a", TypeView(int)),
        ParameterView("b", TypeView(int)),
    )
    assert wrapped_foo_view.return_type == TypeView(int)
