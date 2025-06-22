"""Specialized database types for common use cases."""

from mocksmith.specialized.contact import Email, PhoneNumber
from mocksmith.specialized.geographic import City, CountryCode, State, ZipCode
from mocksmith.specialized.web import URL

__all__ = [
    "URL",
    "City",
    "CountryCode",
    "Email",
    "PhoneNumber",
    "State",
    "ZipCode",
]
