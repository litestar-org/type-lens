from __future__ import annotations

from inspect import Parameter
from typing import Any

from type_lens.parameter_view import ParameterView
from type_lens.type_view import TypeView
from type_lens.types.empty import Empty


def test_param_view() -> None:
    """Test ParameterView."""
    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    param_view = ParameterView.from_parameter(param, {"foo": int})
    assert param_view.name == "foo"
    assert param_view.default is Empty
    assert param_view.type_view.annotation is int


def test_from_parameter_coerces_empty_annotation() -> None:
    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD)

    assert ParameterView.from_parameter(param, {}).type_view == TypeView(Any)


def test_param_view_has_default_predicate() -> None:
    """Test ParameterView.has_default."""
    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    param_view = ParameterView.from_parameter(param, {"foo": int})
    assert param_view.has_default is False

    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD, annotation=int, default=42)
    param_view = ParameterView.from_parameter(param, {"foo": int})
    assert param_view.has_default is True


def test_param_view_repr() -> None:
    assert repr(ParameterView("str")).replace("typing.", "") == "ParameterView('str', TypeView(Any))"
    assert repr(ParameterView("str", TypeView(int))) == "ParameterView('str', TypeView(int))"
    assert (
        repr(ParameterView("str", default=True)).replace("typing.", "")
        == "ParameterView('str', TypeView(Any), default=True)"
    )
