# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-01

### Added
- Initial release of mocksmith (renamed from python-db-types)
- Core database types: VARCHAR, CHAR, TEXT, INTEGER, BIGINT, SMALLINT, DECIMAL, FLOAT, DOUBLE, REAL, TINYINT
- Temporal types: DATE, TIME, TIMESTAMP, DATETIME
- Binary types: BINARY, VARBINARY, BLOB
- Boolean type with flexible parsing
- Full Pydantic v2 integration
- Dataclass integration with validation
- Clean annotation syntax (e.g., `name: Varchar(50)`)
- Automatic type conversion and validation
- **Mock data generation** with `@mockable` decorator
- Type-safe builder pattern for mock generation
- Specialized types (Email, URL, CountryCode, City, State, ZipCode, PhoneNumber)
- Constrained numeric types (PositiveInteger, NonNegativeInteger, etc.)
- Support for Optional fields with probabilistic None generation
- Comprehensive test suite with 100% coverage of mock functionality
- Type hints throughout the codebase

### Changed
- Renamed project from python-db-types to mocksmith
- Removed `nullable` parameter in favor of Python's `Optional` type
- Removed `db_field` function for cleaner API
- Simplified validation to work with Python's type system
- Reorganized namespace to separate core types from specialized types

### Developer Experience
- Added GitHub Actions for CI/CD
- Added automatic release workflow for continuous deployment
- Added semantic versioning with conventional commits
- Added code coverage reporting
- Added PR title validation for conventional commits
- Added comprehensive contributing guidelines

[Unreleased]: https://github.com/gurmeetsaran/mocksmith/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/gurmeetsaran/mocksmith/releases/tag/v0.1.0
