__all__ = (
    "TypeLensError",
    "TypeViewError",
    "ParameterViewError",
)


class TypeLensError(Exception):
    """Base class for library exceptions."""


class TypeViewError(TypeLensError):
    """Base class for TypeView exceptions."""


class ParameterViewError(TypeLensError):
    """Base class for ParameterView exceptions."""
