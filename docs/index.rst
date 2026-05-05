=========
Type Lens
=========

Introduction
============

`type-lens` is a library for introspecting Python type annotations at runtime. It aims to provide a unified, ergonomic
API that works consistently across Python versions, smoothing over the many version-specific quirks and behavioral
differences in Python's `typing` module.

The library is built around three core classes:

- :class:`~type_lens.TypeView`: Represents a type annotation and exposes a rich set of properties for inspection.
- :class:`~type_lens.ParameterView`: Represents a parameter and its associated type information, in the context of a signature.
- :class:`~type_lens.CallableView`: Represents a whole callable signature, including all its parameters and return type.

Comparison with Related Libraries
==================================

vs. ``typing-extensions``
--------------------------

``typing-extensions`` backports new typing constructs (``TypeAlias``, ``Protocol``, ``ParamSpec``, etc.) to older Python versions.
It is largely a compatibility shim which let users *write* new-style annotations on older Python, but not provide a runtime
introspection API. ``type-lens`` uses ``typing-extensions`` internally and is fully complementary to it.

vs. ``typing_inspect``
-----------------------

``typing_inspect`` provides standalone functions (``is_optional_type()``, ``get_args()``, ``get_parameters()``, etc.) for inspecting
individual types. It appears to be designed to provide some missing unit functionality, but does not attempt to abstract
over the type system itself, nor attempt to normalize behavior across python versions. ``type-lens`` is designed to be a complete,
version-normalized introspection layer rather than a collection of utilities.

Python Version Quirks Handled Transparently
============================================

Python's typing system has accumulated numerous version-specific inconsistencies. For example:

- Union syntax (``int | str``) (Python >= 3.10)
- ``Annotated`` + ``Optional`` bug `#90353 <https://github.com/python/cpython/issues/90353>`_ (Python < 3.11)
- ``collections.abc`` types not generic (Python < 3.10)
- ``get_type_hints`` forward-reference evaluation (Python < 3.10)

``type-lens`` tries to provide an interface that is able to consistently model the type system at runtime, where a naive
implementation might work differently across different python version.

.. toctree::
    :titlesonly:
    :caption: Documentation
    :hidden:

    usage/index
    reference/index

.. toctree::
    :titlesonly:
    :caption: Development
    :hidden:

    changelog
    contribution-guide
    Available Issues <https://github.com/search?q=user%3Alitestar-org+state%3Aopen+label%3A%22good+first+issue%22+++no%3Aassignee+repo%3A%22type-lens%22&type=issues>
    Code of Conduct <https://github.com/litestar-org/.github?tab=coc-ov-file#readme>
