<!-- markdownlint-disable -->
<p align="center">
  <img src="https://raw.githubusercontent.com/litestar-org/branding/473f54621e55cde9acbb6fcab7fc03036173eb3d/assets/Branding%20-%20PNG%20-%20Transparent/Logo%20-%20Banner%20-%20Inline%20-%20Light.png" alt="Litestar Logo - Light" width="100%" height="auto" />
</p>

`type-lens` is a library for introspecting Python type annotations at runtime. It aims to provide a unified, ergonomic
API that works consistently across Python versions, smoothing over the many version-specific quirks and behavioral
differences in Python's `typing` module.

The library is built around three core classes:

- **`TypeView`**: Represents a type annotation and exposes a rich set of properties for inspection.
- **`ParameterView`**: Represents a parameter and its associated type information, in the context of a signature.
- **`CallableView`**: Represents a whole callable signature, including all its parameters and return type.

See the [documentation](https://docs.type-lens.litestar.dev) and
[GitHub repository](https://github.com/litestar-org/type-lens) for full details.

[litestar-org]: https://github.com/litestar-org
[contributing]: https://docs.type-lens.litestar.dev/latest/contribution-guide.html
[discord]: https://discord.gg/litestar
[litestar-discussions]: https://github.com/orgs/litestar-org/discussions
[project-discussions]: https://github.com/litestar-org/type-lens/discussions
[project-docs]: https://docs.type-lens.litestar.dev
