# CHANGELOG


## v1.0.0 (2025-06-22)

### Chores

- Bump version to 0.2.0 and enable major version bumps
  ([`88270ae`](https://github.com/gurmeetsaran/mocksmith/commit/88270aea5db9a26eceabd4492a9e78ddb1cd988e))

- Set major_on_zero = true to allow proper versioning - Bump to 0.2.0 to move past the existing
  0.1.0 tag

- Update readme
  ([`ad42dde`](https://github.com/gurmeetsaran/mocksmith/commit/ad42dde0e95b9b039b004e963141c29ba51ddebc))

- **deps-dev**: Bump the development group with 3 updates
  ([#7](https://github.com/gurmeetsaran/mocksmith/pull/7),
  [`92c5f0c`](https://github.com/gurmeetsaran/mocksmith/commit/92c5f0c1555b29e893d6e3f4aa24df04963273a8))

Updates the requirements on [pytest-cov](https://github.com/pytest-dev/pytest-cov),
  [black](https://github.com/psf/black) and [isort](https://github.com/PyCQA/isort) to permit the
  latest version.

Updates `pytest-cov` to 6.2.1 -
  [Changelog](https://github.com/pytest-dev/pytest-cov/blob/master/CHANGELOG.rst) -
  [Commits](https://github.com/pytest-dev/pytest-cov/compare/v5.0.0...v6.2.1)

Updates `black` to 25.1.0 - [Release notes](https://github.com/psf/black/releases) -
  [Changelog](https://github.com/psf/black/blob/main/CHANGES.md) -
  [Commits](https://github.com/psf/black/compare/24.8.0...25.1.0)

Updates `isort` to 6.0.1 - [Release notes](https://github.com/PyCQA/isort/releases) -
  [Changelog](https://github.com/PyCQA/isort/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/PyCQA/isort/compare/5.12.0...6.0.1)

--- updated-dependencies: - dependency-name: pytest-cov dependency-version: 6.2.1

dependency-type: direct:development

dependency-group: development

- dependency-name: black dependency-version: 25.1.0

- dependency-name: isort dependency-version: 6.0.1

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump the development group with 4 updates
  ([#4](https://github.com/gurmeetsaran/mocksmith/pull/4),
  [`28136e5`](https://github.com/gurmeetsaran/mocksmith/commit/28136e55c7c1e423de9b1e97e4dc2c509ce1caf0))

Updates the requirements on [pytest](https://github.com/pytest-dev/pytest),
  [pytest-cov](https://github.com/pytest-dev/pytest-cov), [ruff](https://github.com/astral-sh/ruff)
  and [black](https://github.com/psf/black) to permit the latest version.

Updates `pytest` to 8.3.5 - [Release notes](https://github.com/pytest-dev/pytest/releases) -
  [Changelog](https://github.com/pytest-dev/pytest/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pytest-dev/pytest/compare/7.0.0...8.3.5)

Updates `pytest-cov` to 5.0.0 -
  [Changelog](https://github.com/pytest-dev/pytest-cov/blob/master/CHANGELOG.rst) -
  [Commits](https://github.com/pytest-dev/pytest-cov/compare/v4.0.0...v5.0.0)

Updates `ruff` to 0.11.13 - [Release notes](https://github.com/astral-sh/ruff/releases) -
  [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/astral-sh/ruff/compare/v0.1.0...0.11.13)

Updates `black` to 24.8.0 - [Release notes](https://github.com/psf/black/releases) -
  [Changelog](https://github.com/psf/black/blob/main/CHANGES.md) -
  [Commits](https://github.com/psf/black/compare/23.1a1...24.8.0)

--- updated-dependencies: - dependency-name: pytest dependency-version: 8.3.5

dependency-type: direct:development

dependency-group: development

- dependency-name: pytest-cov dependency-version: 5.0.0

- dependency-name: ruff dependency-version: 0.11.13

- dependency-name: black dependency-version: 24.8.0

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: Gurmeet Saran <gurmeetx@gmail.com>

- **deps-dev**: Update pre-commit requirement from ^3.0.0 to ^4.2.0
  ([#6](https://github.com/gurmeetsaran/mocksmith/pull/6),
  [`9dc9724`](https://github.com/gurmeetsaran/mocksmith/commit/9dc972449bfc4d4abcfefe6db0bbad6d5cfb16b2))

Updates the requirements on [pre-commit](https://github.com/pre-commit/pre-commit) to permit the
  latest version. - [Release notes](https://github.com/pre-commit/pre-commit/releases) -
  [Changelog](https://github.com/pre-commit/pre-commit/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/pre-commit/pre-commit/compare/v3.0.0...v4.2.0)

--- updated-dependencies: - dependency-name: pre-commit dependency-version: 4.2.0

dependency-type: direct:development

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Continuous Integration

- Fix auto release
  ([`2fb3aa3`](https://github.com/gurmeetsaran/mocksmith/commit/2fb3aa313c7636f778aa538d396b5bdd48e6351f))

- Fix building package before publishing
  ([`bde7f18`](https://github.com/gurmeetsaran/mocksmith/commit/bde7f18d95e30415762a07ee168fb855ba106838))

- Fix flake test case test_pydantic_optional_fields
  ([`92a24b7`](https://github.com/gurmeetsaran/mocksmith/commit/92a24b7a084abb8b45e9322bcb0a2a645d69bb63))

- Fixing release package error
  ([`75bed0a`](https://github.com/gurmeetsaran/mocksmith/commit/75bed0aa62dce6c5200b21c92a1e298b39ee031e))

- Updated test cases and github action for release management + pyright integration
  ([#1](https://github.com/gurmeetsaran/mocksmith/pull/1),
  [`a4423b5`](https://github.com/gurmeetsaran/mocksmith/commit/a4423b52018e20cadf26de1cef5d03ddec0dd10e))

* add release workflow and github action

* fix: apply linter fixes for tests

* fix: resolve all linting issues

* add pyright

* feat: switch to Poetry and add pyright type checking

- Replace setuptools with Poetry for dependency management - Add pyright for type checking
  (replacing mypy) - Update all GitHub Actions workflows to use Poetry - Fix type checking errors
  and Python 3.8 compatibility - Add Makefile for common development tasks - Add TESTING.md
  documentation explaining coverage approach - Configure coverage threshold at 59% (accounts for
  skipped tests on Python 3.8) - Fix Poetry installation on Windows CI - Update .gitignore to
  exclude poetry.lock - Fix pydantic example type ignore comment - Use shell: bash for
  cross-platform compatibility - Skip failing dataclass validation tests on Python 3.8

Note: Coverage varies by Python version (59% on 3.8, 66% on 3.9+) due to

dataclass validation limitations on Python 3.8.

- **deps**: Bump codecov/codecov-action from 4 to 5
  ([#3](https://github.com/gurmeetsaran/mocksmith/pull/3),
  [`c357a8e`](https://github.com/gurmeetsaran/mocksmith/commit/c357a8e893d0064bef9fb95fbfe4376314e1c779))

Bumps [codecov/codecov-action](https://github.com/codecov/codecov-action) from 4 to 5. - [Release
  notes](https://github.com/codecov/codecov-action/releases) -
  [Changelog](https://github.com/codecov/codecov-action/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/codecov/codecov-action/compare/v4...v5)

--- updated-dependencies: - dependency-name: codecov/codecov-action dependency-version: '5'

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump softprops/action-gh-release from 1 to 2
  ([#2](https://github.com/gurmeetsaran/mocksmith/pull/2),
  [`691155f`](https://github.com/gurmeetsaran/mocksmith/commit/691155fdb40120c00cad383342a8660b1446b9d5))

Bumps [softprops/action-gh-release](https://github.com/softprops/action-gh-release) from 1 to 2. -
  [Release notes](https://github.com/softprops/action-gh-release/releases) -
  [Changelog](https://github.com/softprops/action-gh-release/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/softprops/action-gh-release/compare/v1...v2)

--- updated-dependencies: - dependency-name: softprops/action-gh-release dependency-version: '2'

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- Add constrained types for int ([#5](https://github.com/gurmeetsaran/mocksmith/pull/5),
  [`7670767`](https://github.com/gurmeetsaran/mocksmith/commit/7670767b020d72f85560b2ee965ea0410b9fd7a4))

add constraned types for int

- Add mock data generation with faker library
  ([#10](https://github.com/gurmeetsaran/mocksmith/pull/10),
  [`6c98102`](https://github.com/gurmeetsaran/mocksmith/commit/6c98102b6f9e7fcb321495383d9f592649ab64f0))

* add mocking

- Add tinyint + constrained tinyint ([#8](https://github.com/gurmeetsaran/mocksmith/pull/8),
  [`cfc3d51`](https://github.com/gurmeetsaran/mocksmith/commit/cfc3d512087d6706b10d22f21246fdfc2dbcc53f))

add tinyint

- Add TINYINT, REAL types and Numeric alias with enhanced validation
  ([#9](https://github.com/gurmeetsaran/mocksmith/pull/9),
  [`66baf28`](https://github.com/gurmeetsaran/mocksmith/commit/66baf2878987343a450c68f3fa80340bfa5f8c62))

add support for tinyint and real type

- Add UUID type and reorganize specialized types
  ([`e5b723f`](https://github.com/gurmeetsaran/mocksmith/commit/e5b723ffacd98fd831eecc5e353b3dd837b6fba5))

This commit includes: - Added UUID type to specialized types - Moved URL from contact.py to web.py
  for better organization - Fixed flaky tests for optional fields

BREAKING CHANGE: URL import path changed from mocksmith.specialized.contact to mocksmith.specialized

- Added release + updated package name to mocksmith
  ([#11](https://github.com/gurmeetsaran/mocksmith/pull/11),
  [`0cd1941`](https://github.com/gurmeetsaran/mocksmith/commit/0cd1941416d6c0ff613dce72fb5a93784ecdaa2e))

* change project name to mocksmith

* add auto release for package

- Moved URL to web.py
  ([`8a31f9d`](https://github.com/gurmeetsaran/mocksmith/commit/8a31f9d5d93a47be0e4c4b0ccaf6b2ca3e872120))

### Refactoring

- Remove unneeded file
  ([`83a66df`](https://github.com/gurmeetsaran/mocksmith/commit/83a66df49bad7e61b1b9b4e6299ca98e20c3d3a3))

### BREAKING CHANGES

- Url import path changed from mocksmith.specialized.contact to mocksmith.specialized
