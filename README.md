# type-lens

<div align="center">

| Project   |     | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------- | :-- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CI/CD     |     | [![Latest Release](https://github.com/jolt-org/type-lens/actions/workflows/publish.yaml/badge.svg)](https://github.com/jolt-org/type-lens/actions/workflows/publish.yaml) [![Tests And Linting](https://github.com/jolt-org/type-lens/actions/workflows/ci.yaml/badge.svg)](https://github.com/jolt-org/type-lens/actions/workflows/ci.yaml) [![Documentation Building](https://github.com/jolt-org/type-lens/actions/workflows/docs.yaml/badge.svg)](https://github.com/jolt-org/type-lens/actions/workflows/docs.yaml)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Quality   |     | [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=jolt-org_type-lens&metric=coverage)](https://sonarcloud.io/summary/new_code?id=jolt-org_type-lens) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=jolt-org_type-lens&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=jolt-org_type-lens) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=jolt-org_type-lens&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=jolt-org_type-lens) [![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=jolt-org_type-lens&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=jolt-org_type-lens) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=jolt-org_type-lens&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=jolt-org_type-lens)                                                                                                  |
| Community |     | [![Discord](https://img.shields.io/discord/1149784127659319356?labelColor=F50057&color=202020&label=chat%20on%20discord&logo=discord&logoColor=202020)](https://discord.gg/XpFNTjjtTK)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Meta      |     | [![Jolt Project](https://img.shields.io/badge/Jolt%20Org-%E2%AD%90-F50057.svg?logo=python&labelColor=F50057&color=202020&logoColor=202020)](https://github.com/jolt-org/) [![types - Mypy](https://img.shields.io/badge/types-Mypy-F50057.svg?logo=python&labelColor=F50057&color=202020&logoColor=202020)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-F50057.svg?logo=python&labelColor=F50057&color=202020&logoColor=202020)](https://spdx.org/licenses/) [![Jolt Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23202020.svg?&logo=github&logoColor=202020&labelColor=F50057)](https://github.com/sponsors/jolt-org) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json&labelColor=F50057)](https://github.com/astral-sh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=python&labelColor=F50057&logoColor=202020)](https://github.com/psf/black) |

</div>

## About

This project is a template repository for [Jolt][jolt-org] projects. It is designed to be a starting point for
any project that is a part of the Jolt organization.

## Usage

- [Install copier](https://copier.readthedocs.io/en/stable/#installation)
- `$ copier copy gh:jolt-org/project-template $new-project-name`
- Answer questions.

## New project checklist

- [ ] Create the https://github.com/jolt-org/type-lens repository.
- [ ] If using docs: Create the https://github.com/jolt-org/type-lens-docs-preview repository.
- [ ] If not using docs: remove `.github/workflows/docs-preview.yaml`.
- [ ] Update the [README.md](README.md) file with the project-specific information.
- [ ] Initialize git repository: `$ git init`
- [ ] Stage the files: `$ git add ."`
- [ ] Install pre-commit hooks: `$ pre-commit install`
- [ ] Run pre-commit hooks: `$ pre-commit run --all-files`
- [ ] Stage any files that were modified by the pre-commit hooks: `$ git add .`
- [ ] Commit the changes: `$ git commit -m "Initial commit"`
- [ ] Add the remote: `$ git remote add origin git@github.com:jolt-org/type-lens.git`
- [ ] Push the changes: `$ git push -u origin main`

## Contributing

All [Jolt][jolt-org] projects will always be a community-centered, available for contributions of any size.

Before contributing, please review the [contribution guide][contributing].

If you have any questions, reach out to us on [Discord][discord], our org-wide [GitHub discussions][jolt-discussions] page,
or the [project-specific GitHub discussions page][project-discussions].

<hr>

<!-- markdownlint-disable -->
<p align="center">
  <!-- github-banner-start -->
  <img src="https://raw.githubusercontent.com/jolt-org/meta/2901c9c5c5895a83fbfa56944c33bca287f88d42/branding/SVG%20-%20Transparent/logo-full-wide.svg" alt="Litestar Logo - Light" width="20%" height="auto" />
  <br>A <a href="https://github.com/jolt-org">Jolt Organization</a> Project
  <!-- github-banner-end -->
</p>

[jolt-org]: https://github.com/jolt-org
[contributing]: https://docs.type-lens.jolt.rs/latest/contribution-guide.html
[discord]: https://discord.gg/XpFNTjjtTK
[jolt-discussions]: https://github.com/orgs/jolt-org/discussions
[project-discussions]: https://github.com/jolt-org/type-lens/discussions
[project-docs]: https://docs.type-lens.jolt.rs
[install-guide]: https://docs.type-lens.jolt.rs/latest/#installation
[newrepo]: https://github.com/organizations/jolt-org/repositories/new?template=type-lens
