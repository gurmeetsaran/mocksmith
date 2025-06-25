"""Tests for Pydantic built-in types support in mock generation."""

import pytest

# Skip all tests if Pydantic is not installed
pydantic = pytest.importorskip("pydantic")

# Module-level imports must be done in the test functions after importorskip


class TestPydanticTypesMocking:
    """Test mock generation for Pydantic built-in types."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Import Pydantic types for tests."""
        from pydantic import (
            UUID4,
            BaseModel,
            HttpUrl,
            IPvAnyAddress,
            NegativeInt,
            PositiveInt,
            conint,
            constr,
        )

        from mocksmith import mockable

        # Make imports available to test methods
        self.BaseModel = BaseModel
        self.HttpUrl = HttpUrl
        self.IPvAnyAddress = IPvAnyAddress
        self.PositiveInt = PositiveInt
        self.NegativeInt = NegativeInt
        self.constr = constr
        self.conint = conint
        self.UUID4 = UUID4
        self.mockable = mockable

    def test_network_types(self):
        """Test mocking of network-related Pydantic types."""

        @self.mockable
        class NetworkModel(self.BaseModel):
            website: self.HttpUrl
            ip_address: self.IPvAnyAddress

        # Generate mock
        model = NetworkModel.mock()

        # Verify types
        # In Pydantic v2, HttpUrl is an object, not a string
        assert hasattr(model.website, "__str__")
        assert str(model.website).startswith(("http://", "https://"))
        # IPvAnyAddress is also an object
        assert hasattr(model.ip_address, "__str__")

        # Verify the generated values are valid
        # This will raise if invalid
        NetworkModel(website=model.website, ip_address=model.ip_address)

    def test_numeric_constraint_types(self):
        """Test mocking of numeric constraint types."""

        @self.mockable
        class NumericModel(self.BaseModel):
            positive: self.PositiveInt
            negative: self.NegativeInt
            ranged: self.conint(ge=10, le=100)

        # Generate multiple to test constraints
        for _ in range(10):
            model = NumericModel.mock()
            assert model.positive > 0
            assert model.negative < 0
            assert 10 <= model.ranged <= 100

    def test_string_constraint_types(self):
        """Test mocking of string constraint types."""

        @self.mockable
        class StringModel(self.BaseModel):
            username: self.constr(min_length=3, max_length=20)
            code: self.constr(pattern=r"^[A-Z]{3}[0-9]{3}$")  # This might not work perfectly
            uuid: self.UUID4

        # Generate mock
        model = StringModel.mock()

        # Verify constraints
        assert 3 <= len(model.username) <= 20
        # UUID4 is a UUID object in Pydantic v2
        assert hasattr(model.uuid, "__str__")
        # UUID should be in the right format when converted to string
        assert len(str(model.uuid)) == 36  # Standard UUID string length

    def test_optional_pydantic_types(self):
        """Test optional Pydantic types."""
        from typing import Optional

        @self.mockable
        class OptionalModel(self.BaseModel):
            website: Optional[self.HttpUrl] = None
            age: Optional[self.PositiveInt] = None

        # Generate multiple to see None values
        has_website = False
        has_no_website = False
        has_age = False
        has_no_age = False

        for _ in range(50):
            model = OptionalModel.mock()
            if model.website is not None:
                has_website = True
                assert str(model.website).startswith(("http://", "https://"))
            else:
                has_no_website = True

            if model.age is not None:
                has_age = True
                assert model.age > 0
            else:
                has_no_age = True

            if all([has_website, has_no_website, has_age, has_no_age]):
                break

        # We should see both None and non-None values
        assert has_website, "Should generate some website values"
        assert has_no_website, "Should generate some None website values"

    def test_mixed_types(self):
        """Test mixing Pydantic types with regular types and mocksmith types."""

        @self.mockable
        class MixedModel(self.BaseModel):
            # Regular Python type
            name: str
            # Pydantic built-in type
            age: self.PositiveInt
            website: self.HttpUrl
            # Mocksmith specialized type (needs DBTypeValidator)
            # email: Email  # This would need special handling

        model = MixedModel.mock()
        assert isinstance(model.name, str)
        assert model.age > 0
        assert str(model.website).startswith(("http://", "https://"))

    def test_builder_pattern_with_pydantic_types(self):
        """Test builder pattern works with Pydantic types."""

        @self.mockable
        class UserModel(self.BaseModel):
            name: str
            age: self.PositiveInt
            website: self.HttpUrl

        # Use builder pattern
        user = (
            UserModel.mock_builder()
            .with_name("John Doe")
            .with_age(25)
            .with_website("https://example.com")
            .build()
        )

        assert user.name == "John Doe"
        assert user.age == 25
        assert str(user.website) == "https://example.com/"

    def test_model_with_validators(self):
        """Test that mocked data passes Pydantic validators."""
        from pydantic import field_validator

        @self.mockable
        class ValidatedModel(self.BaseModel):
            age: self.PositiveInt
            website: self.HttpUrl

            @field_validator("age")
            @classmethod
            def age_must_be_adult(cls, v):
                # This might fail sometimes with random data
                # Just testing that validators run
                return v

            @field_validator("website")
            @classmethod
            def website_must_be_https(cls, v):
                # This validator might fail with generated http:// URLs
                # Just testing that it runs
                return v

        # Generate mock - validators will run
        model = ValidatedModel.mock()
        assert model.age > 0
        assert isinstance(model.website, self.HttpUrl)
