from __future__ import annotations

from inspect import Parameter

import pytest

from type_lens.exc import ParameterViewError
from type_lens.parameter_view import ParameterView
from type_lens.types import Empty


def test_param_view() -> None:
    """Test ParameterView."""
    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    param_view = ParameterView.from_parameter(param, {"foo": int})
    assert param_view.name == "foo"
    assert param_view.default is Empty
    assert param_view.type_view.annotation is int


def test_param_view_raises_improperly_configured_if_no_annotation() -> None:
    """Test ParameterView raises ImproperlyConfigured if no annotation."""
    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD)
    with pytest.raises(ParameterViewError):
        ParameterView.from_parameter(param, {})


def test_param_view_has_default_predicate() -> None:
    """Test ParameterView.has_default."""
    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    param_view = ParameterView.from_parameter(param, {"foo": int})
    assert param_view.has_default is False

    param = Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD, annotation=int, default=42)
    param_view = ParameterView.from_parameter(param, {"foo": int})
    assert param_view.has_default is True
