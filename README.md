<!-- markdownlint-disable -->
<p align="center">
  <!-- github-banner-start -->
  <img src="https://raw.githubusercontent.com/litestar-org/branding/main/assets/Branding%20-%20SVG%20-%20Transparent/Type%20Lens%20-%20Banner%20-%20Inline%20-%20Light.svg#gh-light-mode-only" alt="Litestar Logo - Light" width="100%" height="auto" />
  <img src="https://raw.githubusercontent.com/litestar-org/branding/main/assets/Branding%20-%20SVG%20-%20Transparent/Type%20Lens%20-%20Banner%20-%20Inline%20-%20Dark.svg#gh-dark-mode-only" alt="Litestar Logo - Dark" width="100%" height="auto" />
  <!-- github-banner-end -->
</p>
<!-- markdownlint-restore -->

<div align="center">

| Project   |     | Status                                                                                                                                                                                                                                                                                                                                                                                      |
| --------- | :-- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CI/CD     |     | [![Latest Release](https://github.com/litestar-org/type-lens/actions/workflows/publish.yml/badge.svg)](https://github.com/litestar-org/type-lens/actions/workflows/publish.yml) [![ci](https://github.com/litestar-org/type-lens/actions/workflows/ci.yml/badge.svg)](https://github.com/litestar-org/type-lens/actions/workflows/ci.yml) [![Documentation Building](https://github.com/litestar-org/type-lens/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/litestar-org/type-lens/actions/workflows/docs.yml) |
| Package   |     | [![PyPI - Version](https://img.shields.io/pypi/v/type-lens?labelColor=202235&color=edb641&logo=python&logoColor=edb641)](https://badge.fury.io/py/litestar) ![PyPI - Support Python Versions](https://img.shields.io/pypi/pyversions/type-lens?labelColor=202235&color=edb641&logo=python&logoColor=edb641) ![type-lens PyPI - Downloads](https://img.shields.io/pypi/dm/type-lens?logo=python&label=package%20downloads&labelColor=202235&color=edb641&logoColor=edb641) |
| Community |     | [![Discord](https://img.shields.io/discord/919193495116337154?labelColor=202235&color=edb641&label=chat%20on%20discord&logo=discord&logoColor=edb641)](https://discord.gg/litestar) |

</div>

## About

`type-lens` is a library for introspecting Python type annotations at runtime. It aims to provide a unified, ergonomic
API that works consistently across Python versions, smoothing over the many version-specific quirks and behavioral
differences in Python's `typing` module.

The library is built around three core classes:

- **`TypeView`**: Represents a type annotation and exposes a rich set of properties for inspection.
- **`ParameterView`**: Represents a parameter and its associated type information, in the context of a signature.
- **`CallableView`**: Represents a whole callable signature, including all its parameters and return type.

### Examples

```python
from typing import Annotated, Optional, Sequence, Union
from type_lens import TypeView, CallableView

# Union detection works regardless of syntax or Python version
TypeView(int | str).is_union            # True  (3.10+ pipe syntax)
TypeView(Union[int, str]).is_union      # True  (all versions)

# Optional / None detection
TypeView(Optional[int]).is_optional     # True
TypeView(int | None).is_optional        # True

# Annotated metadata is extracted automatically
view = TypeView(Annotated[int, "positive"])
view.annotation   # <class 'int'>
view.metadata     # ('positive',)
view.is_annotated # True

# Collection and mapping classification
TypeView(list[int]).is_collection               # True
TypeView(dict[str, int]).is_mapping             # True
TypeView(Sequence[str]).is_collection           # True
TypeView(str).is_non_string_collection          # False

# Traverse generic args as TypeViews
inner = TypeView(dict[str, list[int]]).inner_types
# (TypeView(str), TypeView(list[int]))
inner[1].inner_types
# (TypeView(int),)

# Resolve abstract types to instantiable concrete types
TypeView(Sequence[int]).instantiable_origin     # <class 'list'>
TypeView(Mapping[str, int]).instantiable_origin # <class 'dict'>

# Strip Optional to get the underlying type
TypeView(int | None).strip_optional()           # TypeView(int)

# Type alias support (3.12 new-style or typing_extensions)
# type Alias = list[int]
TypeView(Alias).is_type_alias                   # True
TypeView(Alias).strip_type_alias()              # TypeView(list[int])

# Inspect callables
def process(items: list[str], limit: int = 10) -> dict[str, int]: ...

view = CallableView.from_callable(process)
view.return_type                    # TypeView(dict[str, int])
view.parameters[0].name            # 'items'
view.parameters[0].type_view       # TypeView(list[str])
view.parameters[1].has_default     # True
```

### How it compares to related libraries

**vs. `typing-extensions`**

`typing-extensions` backports new typing constructs (`TypeAlias`, `Protocol`, `ParamSpec`, etc.) to older Python versions.
It is largely a compatibility shim which let users *write* new-style annotations on older Python, but not provide a runtime
introspection API. `type-lens` uses `typing-extensions` internally and is fully complementary to it.

**vs. `typing_inspect`**

`typing_inspect` provides standalone functions (`is_optional_type()`, `get_args()`, `get_parameters()`, etc.) for inspecting
individual types. It appears to be designed to provide some missing unit functionality, but does not attempt to abstract
over the type system itself, nor attempt to normalize behavior across python versions. `type-lens` is designed to be a complete,
version-normalized introspection layer rather than a collection of utilities.

### Python version-specific quirks

Python's typing system has accumulated numerous version-specific inconsistencies. For example:

- Union syntax (``int | str``) (Python >= 3.10)
- `Annotated` + `Optional` bug [#90353](https://github.com/python/cpython/issues/90353) (Python < 3.11)
- `collections.abc` types not generic (Python < 3.10)
- `get_type_hints` forward-reference evaluation (Python < 3.10)

`type-lens` tries to provide an interface that is able to consistently model the type system at runtime, where a naive
implementation might work differently across different python version.

## Installation

```shell
pip install type-lens
```

## Contributing

All [Litestar Organization][litestar-org] projects will always be a community-centered, available for contributions of any size.

Before contributing, please review the [contribution guide][contributing].

If you have any questions, reach out to us on [Discord][discord], our org-wide [GitHub discussions][litestar-discussions] page,
or the [project-specific GitHub discussions page][project-discussions].

<hr>

<!-- markdownlint-disable -->
<p align="center">
  <!-- github-banner-start -->
  <img src="https://raw.githubusercontent.com/litestar-org/branding/main/assets/Branding%20-%20SVG%20-%20Transparent/Organization%20Project%20-%20Banner%20-%20Inline%20-%20Dark.svg" alt="Litestar Logo - Light" width="40%" height="auto" />
  <br>An official <a href="https://github.com/litestar-org">Litestar Organization</a> Project
  <!-- github-banner-end -->
</p>

[litestar-org]: https://github.com/litestar-org
[contributing]: https://docs.type-lens.litestar.dev/latest/contribution-guide.html
[discord]: https://discord.gg/litestar
[litestar-discussions]: https://github.com/orgs/litestar-org/discussions
[project-discussions]: https://github.com/litestar-org/type-lens/discussions
[project-docs]: https://docs.type-lens.litestar.dev
