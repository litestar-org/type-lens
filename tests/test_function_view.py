from typing import Any, Optional, Union

from typing_extensions import Annotated

from type_lens import FunctionView, ParameterView, TypeView


def test_no_return_annotation() -> None:
    def fn():  # type: ignore[no-untyped-def]
        return

    function_view = FunctionView.from_type_hints(fn)
    assert function_view.parameters == ()
    assert function_view.return_type == TypeView(None)


def test_return_annotation() -> None:
    def fn() -> int:
        return 4

    function_view = FunctionView.from_type_hints(fn)
    assert function_view.parameters == ()
    assert function_view.return_type == TypeView(int)


def test_untyped_param() -> None:
    def fn(foo):  # type: ignore[no-untyped-def]
        return foo

    function_view = FunctionView.from_type_hints(fn)
    assert function_view.parameters == (ParameterView("foo", TypeView(Any)),)


def test_typed_param() -> None:
    def fn(foo: int) -> int:
        return foo

    function_view = FunctionView.from_type_hints(fn)
    assert function_view.parameters == (ParameterView("foo", TypeView(int)),)


def test_fix_annotated_optional_type_hints() -> None:
    def fn1(foo: Annotated[Optional[int], "d"] = None) -> Optional[int]:
        return foo

    def fn2(foo: Annotated[Optional[int], "d"] = None) -> Optional[int]:
        return foo

    fn_view1 = FunctionView.from_type_hints(fn1, include_extras=True)
    assert fn_view1.parameters == (ParameterView("foo", TypeView(Annotated[Union[int, None], "d"]), default=None),)

    fn_view2 = FunctionView.from_type_hints(fn2, include_extras=True)
    assert fn_view2.parameters == (ParameterView("foo", TypeView(Annotated[Union[int, None], "d"]), default=None),)
