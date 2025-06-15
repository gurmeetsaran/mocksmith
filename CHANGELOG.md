# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of python-db-types
- Core database types: VARCHAR, CHAR, TEXT, INTEGER, BIGINT, SMALLINT, DECIMAL, FLOAT, DOUBLE
- Temporal types: DATE, TIME, TIMESTAMP, DATETIME
- Binary types: BINARY, VARBINARY, BLOB
- Boolean type with flexible parsing
- Full Pydantic v2 integration
- Dataclass integration with validation
- Clean annotation syntax (e.g., `name: Varchar(50)`)
- Automatic type conversion and validation
- Comprehensive test suite
- Type hints throughout the codebase

### Changed
- Removed `nullable` parameter in favor of Python's `Optional` type
- Removed `db_field` function for cleaner API
- Simplified validation to work with Python's type system

### Developer Experience
- Added GitHub Actions for CI/CD
- Added code coverage reporting
- Added PR title validation for conventional commits
- Added comprehensive contributing guidelines

[Unreleased]: https://github.com/gurmeetsaran/python-db-types/commits/main
