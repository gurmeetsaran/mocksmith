"""Tests for Literal type support in mock generation."""

from dataclasses import dataclass
from typing import Literal, Optional

import pytest

from mocksmith.mock_factory import mock_factory

try:
    from pydantic import BaseModel, Field

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None  # type: ignore
    Field = None  # type: ignore


class TestLiteralWithDataclass:
    """Test Literal types with regular dataclasses."""

    def test_string_literal(self):
        """Test string literal values."""

        @dataclass
        class Config:
            environment: Literal["dev", "staging", "prod"]
            log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]

        # Generate multiple mocks to ensure randomness
        mocks = [mock_factory(Config) for _ in range(20)]

        # Check all values are valid
        for mock in mocks:
            assert mock.environment in ["dev", "staging", "prod"]
            assert mock.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

        # Check that we get different values (with high probability)
        environments = {mock.environment for mock in mocks}
        log_levels = {mock.log_level for mock in mocks}
        assert len(environments) > 1  # Should have at least 2 different environments
        assert len(log_levels) > 1  # Should have at least 2 different log levels

    def test_numeric_literal(self):
        """Test numeric literal values."""

        @dataclass
        class Server:
            port: Literal[8080, 8443, 9000]
            workers: Literal[1, 2, 4, 8]

        # Generate multiple mocks
        mocks = [mock_factory(Server) for _ in range(20)]

        # Check all values are valid
        for mock in mocks:
            assert mock.port in [8080, 8443, 9000]
            assert mock.workers in [1, 2, 4, 8]

        # Check randomness
        ports = {mock.port for mock in mocks}
        workers = {mock.workers for mock in mocks}
        assert len(ports) > 1
        assert len(workers) > 1

    def test_mixed_literal(self):
        """Test literal with mixed types."""

        @dataclass
        class Status:
            code: Literal[200, 404, "OK", "NOT_FOUND"]

        # Generate multiple mocks
        mocks = [mock_factory(Status) for _ in range(20)]

        # Check all values are valid
        for mock in mocks:
            assert mock.code in [200, 404, "OK", "NOT_FOUND"]

        # Check we get both string and int values
        types_seen = {type(mock.code) for mock in mocks}
        assert len(types_seen) == 2  # Should see both str and int

    def test_optional_literal(self):
        """Test optional literal values."""

        @dataclass
        class Feature:
            mode: Optional[Literal["read", "write", "read-write"]]

        # Generate multiple mocks
        mocks = [mock_factory(Feature) for _ in range(50)]

        # Count None vs non-None values
        none_count = sum(1 for mock in mocks if mock.mode is None)
        non_none_count = sum(1 for mock in mocks if mock.mode is not None)

        # Should have both None and non-None values
        assert none_count > 0
        assert non_none_count > 0

        # Check non-None values are valid
        for mock in mocks:
            if mock.mode is not None:
                assert mock.mode in ["read", "write", "read-write"]


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not installed")
class TestLiteralWithPydantic:
    """Test Literal types with Pydantic models."""

    def test_pydantic_literal_basic(self):
        """Test basic literal in Pydantic model."""

        class ApiConfig(BaseModel):
            method: Literal["GET", "POST", "PUT", "DELETE"]
            version: Literal["v1", "v2", "v3"]

        # Generate multiple mocks
        mocks = [mock_factory(ApiConfig) for _ in range(20)]

        # Check all values are valid
        for mock in mocks:
            assert mock.method in ["GET", "POST", "PUT", "DELETE"]
            assert mock.version in ["v1", "v2", "v3"]

        # Check randomness
        methods = {mock.method for mock in mocks}
        versions = {mock.version for mock in mocks}
        assert len(methods) > 1
        assert len(versions) > 1

    def test_pydantic_literal_with_field(self):
        """Test literal with Field constraints."""

        class Database(BaseModel):
            engine: Literal["postgres", "mysql", "sqlite"] = Field(description="Database engine")
            pool_size: Literal[5, 10, 20, 50] = Field(description="Connection pool size")

        # Generate multiple mocks
        mocks = [mock_factory(Database) for _ in range(20)]

        # Check all values are valid
        for mock in mocks:
            assert mock.engine in ["postgres", "mysql", "sqlite"]
            assert mock.pool_size in [5, 10, 20, 50]

    def test_pydantic_optional_literal(self):
        """Test optional literal in Pydantic."""

        class Settings(BaseModel):
            theme: Optional[Literal["light", "dark", "auto"]]
            locale: Optional[Literal["en", "es", "fr", "de"]]

        # Generate multiple mocks
        mocks = [mock_factory(Settings) for _ in range(50)]

        # Should have both None and non-None values
        theme_none = sum(1 for mock in mocks if mock.theme is None)
        locale_none = sum(1 for mock in mocks if mock.locale is None)

        assert theme_none > 0
        assert locale_none > 0
        assert theme_none < 50  # Not all should be None
        assert locale_none < 50

        # Check non-None values are valid
        for mock in mocks:
            if mock.theme is not None:
                assert mock.theme in ["light", "dark", "auto"]
            if mock.locale is not None:
                assert mock.locale in ["en", "es", "fr", "de"]


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not installed")
class TestLiteralWithAnnotated:
    """Test Literal types with Annotated and Pydantic constraints."""

    def test_annotated_literal(self):
        """Test literal with Annotated."""
        from typing import Annotated

        @dataclass
        class Task:
            priority: Annotated[Literal["low", "medium", "high"], Field()]
            retries: Annotated[Literal[0, 1, 3, 5], Field(description="Retry count")]

        # Generate multiple mocks
        mocks = [mock_factory(Task) for _ in range(20)]

        # Check all values are valid
        for mock in mocks:
            assert mock.priority in ["low", "medium", "high"]
            assert mock.retries in [0, 1, 3, 5]

        # Check randomness
        priorities = {mock.priority for mock in mocks}
        retries = {mock.retries for mock in mocks}
        assert len(priorities) > 1
        assert len(retries) > 1

    def test_complex_annotated_literal(self):
        """Test complex literal scenarios with Annotated."""
        from typing import Annotated

        @dataclass
        class Service:
            state: Annotated[
                Literal["starting", "running", "stopping", "stopped"],
                Field(description="Service state"),
            ]
            restart_policy: Annotated[
                Optional[Literal["always", "on-failure", "never"]],
                Field(description="Restart policy"),
            ]

        # Generate multiple mocks
        mocks = [mock_factory(Service) for _ in range(30)]

        # Check all values are valid
        for mock in mocks:
            assert mock.state in ["starting", "running", "stopping", "stopped"]
            if mock.restart_policy is not None:
                assert mock.restart_policy in ["always", "on-failure", "never"]

        # Check we get variety in states
        states = {mock.state for mock in mocks}
        assert len(states) >= 2


class TestLiteralEdgeCases:
    """Test edge cases for Literal types."""

    def test_single_value_literal(self):
        """Test literal with single value."""

        @dataclass
        class Constant:
            version: Literal["1.0.0"]
            magic_number: Literal[42]

        # Generate multiple mocks
        mocks = [mock_factory(Constant) for _ in range(5)]

        # All should have the same value
        for mock in mocks:
            assert mock.version == "1.0.0"
            assert mock.magic_number == 42

    def test_boolean_literal(self):
        """Test literal with boolean values."""

        @dataclass
        class Flag:
            enabled: Literal[True]
            disabled: Literal[False]
            maybe: Literal[True, False]

        # Generate multiple mocks
        mocks = [mock_factory(Flag) for _ in range(20)]

        # Check fixed values
        for mock in mocks:
            assert mock.enabled is True
            assert mock.disabled is False
            assert mock.maybe in [True, False]

        # Check maybe has both values
        maybe_values = {mock.maybe for mock in mocks}
        assert len(maybe_values) == 2

    def test_none_in_literal(self):
        """Test literal that includes None as a value."""

        @dataclass
        class NullableState:
            state: Literal["active", "inactive", None]

        # Generate multiple mocks
        mocks = [mock_factory(NullableState) for _ in range(30)]

        # Check all values are valid
        for mock in mocks:
            assert mock.state in ["active", "inactive", None]

        # Should have all three values
        states = {mock.state for mock in mocks}
        assert len(states) == 3
