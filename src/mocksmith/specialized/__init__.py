"""Specialized database types for common use cases."""

from mocksmith.specialized.contact import URL, Email, PhoneNumber
from mocksmith.specialized.geographic import City, CountryCode, State, ZipCode

__all__ = [
    "URL",
    "City",
    "CountryCode",
    "Email",
    "PhoneNumber",
    "State",
    "ZipCode",
]
