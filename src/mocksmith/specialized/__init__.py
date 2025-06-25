"""Specialized database types for common use cases."""

from mocksmith.specialized.contact import PhoneNumber
from mocksmith.specialized.geographic import City, CountryCode, State, ZipCode

__all__ = [
    "City",
    "CountryCode",
    "PhoneNumber",
    "State",
    "ZipCode",
]
