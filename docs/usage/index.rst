===========
Usage Guide
===========

Installation
============

.. code-block:: shell

    pip install type-lens

Core Concepts
=============

TypeView
--------

:class:`~type_lens.TypeView` is the central class. It wraps any type annotation and exposes a
consistent, property-based API for introspection.

.. code-block:: python

    from typing import Annotated, Optional, Union
    from type_lens import TypeView

    # Basic properties
    view = TypeView(int)
    view.annotation          # <class 'int'>
    view.is_optional         # False
    view.is_union            # False
    view.is_collection       # False

    # Union types — works regardless of Python version or syntax
    TypeView(int | str).is_union            # True  (3.10+ pipe syntax)
    TypeView(Union[int, str]).is_union      # True  (all versions)

    # Optional detection
    TypeView(Optional[int]).is_optional     # True
    TypeView(int | None).is_optional        # True

    # Inner types are recursively wrapped as TypeViews
    view = TypeView(dict[str, list[int]])
    view.inner_types
    # (TypeView(str), TypeView(list[int]))
    view.inner_types[1].inner_types
    # (TypeView(int),)

Annotated Metadata
------------------

:class:`~type_lens.TypeView` automatically unwraps ``Annotated``, ``Required``, and
``NotRequired``, making the inner type and any metadata directly accessible.

.. code-block:: python

    from typing import Annotated
    from type_lens import TypeView

    view = TypeView(Annotated[int, "positive", lambda x: x > 0])
    view.annotation   # <class 'int'>
    view.metadata     # ('positive', <lambda>)
    view.is_annotated # True

    # Required/NotRequired from TypedDict
    from typing import Required, NotRequired
    TypeView(Required[str]).is_required         # True
    TypeView(NotRequired[str]).is_not_required  # True

Collections and Mappings
------------------------

.. code-block:: python

    from collections.abc import Sequence, Mapping
    from type_lens import TypeView

    TypeView(list[int]).is_collection               # True
    TypeView(dict[str, int]).is_mapping             # True
    TypeView(Sequence[str]).is_collection           # True
    TypeView(str).is_non_string_collection          # False
    TypeView(bytes).is_non_string_collection        # False

    # Resolve abstract types to a concrete instantiable type
    TypeView(Sequence[int]).instantiable_origin     # <class 'list'>
    TypeView(Mapping[str, int]).instantiable_origin # <class 'dict'>

Type Aliases
------------

Both Python 3.12 native ``type`` statements and ``typing_extensions.TypeAliasType`` are supported.

.. code-block:: python

    from typing_extensions import TypeAliasType
    from type_lens import TypeView

    Vector = TypeAliasType("Vector", list[float])

    TypeView(Vector).is_type_alias       # True
    TypeView(Vector).strip_type_alias()  # TypeView(list[float])

    # Python 3.12+:
    # type Matrix = list[list[float]]
    # TypeView(Matrix).is_type_alias     # True

Stripping Optional
------------------

.. code-block:: python

    from type_lens import TypeView

    TypeView(int | None).strip_optional()          # TypeView(int)
    TypeView(int | str | None).strip_optional()    # TypeView(int | str)
    TypeView(int).strip_optional()                 # TypeView(int)  (no-op)

Subtype Checks
--------------

:meth:`~type_lens.TypeView.is_subtype_of` handles union types correctly: it returns ``True``
only when *all* members of the union are subtypes of the given type.

.. code-block:: python

    from type_lens import TypeView

    TypeView(bool).is_subtype_of(int)              # True
    TypeView(int | bool).is_subtype_of(int)        # True
    TypeView(int | str).is_subtype_of(int)         # False

    # Check if any inner type is a subtype
    TypeView(list[int]).has_inner_subtype_of(int)  # True

ParameterView
-------------

:class:`~type_lens.ParameterView` wraps an ``inspect.Parameter`` and its resolved annotation.

.. code-block:: python

    import inspect
    from type_lens import ParameterView

    def greet(name: str, count: int = 1) -> str: ...

    sig = inspect.signature(greet)
    hints = {"name": str, "count": int}

    param = ParameterView.from_parameter(sig.parameters["count"], hints)
    param.name          # 'count'
    param.type_view     # TypeView(int)
    param.has_default   # True
    param.default       # 1

CallableView
------------

:class:`~type_lens.CallableView` inspects a callable's full signature, resolving all annotations
(including string forward references) into :class:`~type_lens.TypeView` instances.

.. code-block:: python

    from type_lens import CallableView

    def process(items: list[str], limit: int = 10) -> dict[str, int]: ...

    view = CallableView.from_callable(process)

    view.return_type                    # TypeView(dict[str, int])
    view.parameters[0].name            # 'items'
    view.parameters[0].type_view       # TypeView(list[str])
    view.parameters[1].name            # 'limit'
    view.parameters[1].has_default     # True

``CallableView.from_callable`` also accepts ``globalns`` and ``localns`` keyword arguments,
passed through to ``get_type_hints()`` for resolving forward references.

The Empty Sentinel
------------------

:data:`~type_lens.Empty` is a sentinel used by :class:`~type_lens.ParameterView` to distinguish
"no default provided" from a default of ``None``.

.. code-block:: python

    from type_lens import Empty, EmptyType

    def check_default(value):
        if value is Empty:
            print("no default")

    isinstance(Empty, EmptyType)  # True
