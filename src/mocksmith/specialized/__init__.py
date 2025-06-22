"""Specialized database types for common use cases."""

from mocksmith.specialized.contact import Email, PhoneNumber
from mocksmith.specialized.geographic import City, CountryCode, State, ZipCode
from mocksmith.specialized.web import URL, IPAddress, IPv4Address, IPv6Address

__all__ = [
    "URL",
    "City",
    "CountryCode",
    "Email",
    "IPAddress",
    "IPv4Address",
    "IPv6Address",
    "PhoneNumber",
    "State",
    "ZipCode",
]
