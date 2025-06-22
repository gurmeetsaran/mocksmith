# Mock Data Generation Feature

This document describes the new mock data generation feature for python-db-types.

## Overview

The mock data generation feature allows you to generate realistic fake data for your database types that respects all defined constraints. This is useful for:
- Testing
- Development
- Data seeding
- Demonstrations

## Installation

To use the mock feature, install with the `mock` extra:

```bash
pip install python-db-types[mock]
```

## Basic Usage

### String Types

All string types now have a `mock()` method that generates appropriate fake data:

```python
from db_types import VARCHAR, CHAR, TEXT

# VARCHAR generates length-appropriate data
name = VARCHAR(50)
print(name.mock())  # "John Smith"

# CHAR generates fixed-length data with padding
code = CHAR(5)
print(code.mock())  # "hello" (padded to 5 chars)

# TEXT generates paragraph text
description = TEXT()
print(description.mock())  # "Lorem ipsum dolor sit amet..."
```

### Specialized Types

The library includes specialized types for common use cases:

```python
from db_types import Country, Email, City, ZipCode, PhoneNumber, URL

# Geographic types
country = Country()
print(country.mock())  # "US"

city = City()
print(city.mock())  # "New York"

zip_code = ZipCode()
print(zip_code.mock())  # "10001"

# Contact types
email = Email()
print(email.mock())  # "john.doe@example.com"

phone = PhoneNumber()
print(phone.mock())  # "+1-555-123-4567"

url = URL()
print(url.mock())  # "https://example.com"
```

### Using with Data Models

```python
from dataclasses import dataclass
from db_types import VARCHAR, Email, Country, TEXT

@dataclass
class User:
    username: VARCHAR
    email: Email
    country: Country
    bio: TEXT
    
    def __init__(self):
        self.username = VARCHAR(30)
        self.email = Email()
        self.country = Country()
        self.bio = TEXT(max_length=500)

# Generate mock data for each field
user = User()
mock_user_data = {
    'username': user.username.mock(),
    'email': user.email.mock(),
    'country': user.country.mock(),
    'bio': user.bio.mock()
}
```

## Implementation Status

### Completed
- ✅ Base mock infrastructure with default implementation
- ✅ String types (VARCHAR, CHAR, TEXT)
- ✅ Specialized string types (Country, Email, City, etc.)
- ✅ Default mock generation for all types (via base class)
- ✅ Class-level mock generation with `@mockable` decorator
- ✅ Type-safe builder pattern for mock generation
- ✅ Integration with dataclasses and Pydantic models
- ✅ Smart field name detection for common patterns
- ✅ Optional field handling (returns None sometimes)
- ✅ Tests for mock functionality

### Features
- **Automatic Mock Generation**: Use `@mockable` decorator on any dataclass or Pydantic model
- **Builder Pattern**: Type-safe field setting with `Model.mock_builder().with_field(value).build()`
- **Field Overrides**: Direct overrides with `Model.mock(field=value)`
- **Smart Detection**: Automatically generates appropriate data based on field names (email, phone, etc.)
- **Constraint Respect**: All generated data respects type constraints

## Extending Mock Generation

To add mock support to a new type:

1. Implement the `_generate_mock` method in your type class:

```python
class MyCustomType(DBType[str]):
    def _generate_mock(self, fake: Any) -> str:
        """Generate mock data for this type."""
        # Use the faker instance to generate appropriate data
        return fake.some_method()
```

2. For specialized types, extend an existing type:

```python
from db_types.types.string import VARCHAR

class Username(VARCHAR):
    def __init__(self):
        super().__init__(30)  # Max 30 chars
    
    def _generate_mock(self, fake: Any) -> str:
        """Generate a username."""
        return fake.user_name()[:self.length]
```

## Locale Support

Mock generation uses the Faker library, which supports multiple locales. To generate locale-specific data:

```python
# This feature is planned for future implementation
# email = Email()
# email.mock(locale='fr_FR')  # French email
```

## Notes

- Generated mock data always respects the type's constraints (length, format, etc.)
- The faker library is only loaded when you call the `mock()` method
- Mock generation is deterministic if you set a seed in faker