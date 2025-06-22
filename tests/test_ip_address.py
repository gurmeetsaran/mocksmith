"""Tests for IP address specialized types."""

import pytest

from mocksmith.specialized import IPAddress, IPv4Address, IPv6Address


class TestIPAddress:
    """Test generic IP address type that accepts both IPv4 and IPv6."""

    def test_valid_ipv4(self):
        """Test valid IPv4 addresses."""
        ip_type = IPAddress()

        # Valid IPv4 addresses
        valid_ips = [
            "192.168.1.1",
            "10.0.0.0",
            "172.16.0.1",
            "8.8.8.8",
            "255.255.255.255",
            "0.0.0.0",
        ]

        for ip in valid_ips:
            ip_type.validate(ip)  # Should not raise

    def test_valid_ipv6(self):
        """Test valid IPv6 addresses."""
        ip_type = IPAddress()

        # Valid IPv6 addresses
        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8:85a3::8a2e:370:7334",  # Compressed
            "::1",  # Loopback
            "fe80::1",  # Link local
            "::ffff:192.0.2.1",  # IPv4 mapped
        ]

        for ip in valid_ips:
            ip_type.validate(ip)  # Should not raise

    def test_invalid_ip(self):
        """Test invalid IP addresses."""
        ip_type = IPAddress()

        invalid_ips = [
            "256.256.256.256",  # Out of range
            "192.168.1",  # Incomplete
            "192.168.1.1.1",  # Too many octets
            "not.an.ip.address",  # Not numeric
            "gggg::1",  # Invalid hex
            "192.168.1.1:8080",  # Port included
        ]

        for ip in invalid_ips:
            with pytest.raises(ValueError, match=f"Invalid IP address format: {ip}"):
                ip_type.validate(ip)

    def test_mock_generation(self):
        """Test mock IP address generation."""
        ip_type = IPAddress()

        # Generate several IPs
        for _ in range(20):
            mock_ip = ip_type.mock()
            # Should be valid
            ip_type.validate(mock_ip)
            # Should be either IPv4 or IPv6
            assert ("." in mock_ip) or (":" in mock_ip)

    def test_none_value(self):
        """Test that None is accepted."""
        ip_type = IPAddress()
        ip_type.validate(None)  # Should not raise


class TestIPv4Address:
    """Test IPv4-only address type."""

    def test_valid_ipv4(self):
        """Test valid IPv4 addresses."""
        ip_type = IPv4Address()

        valid_ips = [
            "192.168.1.1",
            "10.0.0.0",
            "172.16.0.1",
            "8.8.8.8",
            "255.255.255.255",
            "0.0.0.0",
        ]

        for ip in valid_ips:
            ip_type.validate(ip)  # Should not raise

    def test_invalid_ipv4(self):
        """Test invalid IPv4 addresses."""
        ip_type = IPv4Address()

        invalid_ips = [
            "256.256.256.256",  # Out of range
            "192.168.1",  # Incomplete
            "192.168.1.1.1",  # Too many octets
            "not.an.ip.address",  # Not numeric
            "2001:db8::1",  # IPv6 address
        ]

        for ip in invalid_ips:
            with pytest.raises(ValueError, match=f"Invalid IPv4 address format: {ip}"):
                ip_type.validate(ip)

    def test_mock_generation(self):
        """Test mock IPv4 address generation."""
        ip_type = IPv4Address()

        # Generate several IPs
        for _ in range(10):
            mock_ip = ip_type.mock()
            # Should be valid IPv4
            ip_type.validate(mock_ip)
            # Should have 3 dots
            assert mock_ip.count(".") == 3
            # All parts should be numeric
            parts = mock_ip.split(".")
            assert len(parts) == 4
            for part in parts:
                assert 0 <= int(part) <= 255

    def test_sql_type(self):
        """Test SQL type generation."""
        ip_type = IPv4Address()
        assert ip_type.sql_type == "VARCHAR(15)"


class TestIPv6Address:
    """Test IPv6-only address type."""

    def test_valid_ipv6(self):
        """Test valid IPv6 addresses."""
        ip_type = IPv6Address()

        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8:85a3::8a2e:370:7334",  # Compressed
            "::1",  # Loopback
            "fe80::1",  # Link local
            "::ffff:192.0.2.1",  # IPv4 mapped
            "2001:db8::8a2e:370:7334",
        ]

        for ip in valid_ips:
            ip_type.validate(ip)  # Should not raise

    def test_invalid_ipv6(self):
        """Test invalid IPv6 addresses."""
        ip_type = IPv6Address()

        invalid_ips = [
            "192.168.1.1",  # IPv4 address
            "gggg::1",  # Invalid hex
            "::1::2",  # Double compression
            "not:an:ipv6:address",  # Not hex
        ]

        for ip in invalid_ips:
            with pytest.raises(ValueError, match=f"Invalid IPv6 address format: {ip}"):
                ip_type.validate(ip)

    def test_mock_generation(self):
        """Test mock IPv6 address generation."""
        ip_type = IPv6Address()

        # Generate several IPs
        for _ in range(10):
            mock_ip = ip_type.mock()
            # Should be valid IPv6
            ip_type.validate(mock_ip)
            # Should contain colons
            assert ":" in mock_ip

    def test_sql_type(self):
        """Test SQL type generation."""
        ip_type = IPv6Address()
        assert ip_type.sql_type == "VARCHAR(39)"


class TestIPAddressIntegration:
    """Test IP address types with dataclasses and Pydantic."""

    def test_dataclass_with_ip(self):
        """Test using IP address types in dataclasses."""
        from dataclasses import dataclass

        from mocksmith import mockable

        @mockable
        @dataclass
        class Server:
            name: str
            ip_address: IPAddress()
            ipv4_address: IPv4Address()
            ipv6_address: IPv6Address()

        # Test mock generation
        server = Server.mock()
        assert isinstance(server.name, str)
        assert isinstance(server.ip_address, str)
        assert isinstance(server.ipv4_address, str)
        assert isinstance(server.ipv6_address, str)

        # Validate generated IPs
        ip_type = IPAddress()
        ipv4_type = IPv4Address()
        ipv6_type = IPv6Address()

        ip_type.validate(server.ip_address)
        ipv4_type.validate(server.ipv4_address)
        ipv6_type.validate(server.ipv6_address)

    def test_pydantic_with_ip(self):
        """Test using IP address types in Pydantic models."""
        try:
            from typing import Annotated

            from pydantic import BaseModel

            from mocksmith import mockable
            from mocksmith.pydantic_v2 import (  # pyright: ignore[reportMissingImports]
                DBTypeValidator,
            )

            @mockable
            class NetworkDevice(BaseModel):
                hostname: str
                management_ip: Annotated[str, DBTypeValidator(IPAddress())]
                primary_ipv4: Annotated[str, DBTypeValidator(IPv4Address())]
                primary_ipv6: Annotated[str, DBTypeValidator(IPv6Address())]

            # Test mock generation
            device = NetworkDevice.mock()
            assert isinstance(device.hostname, str)
            assert isinstance(device.management_ip, str)
            assert isinstance(device.primary_ipv4, str)
            assert isinstance(device.primary_ipv6, str)

            # Test validation with invalid IPs
            with pytest.raises(ValueError):
                NetworkDevice(
                    hostname="router1",
                    management_ip="invalid.ip",
                    primary_ipv4="192.168.1.1",
                    primary_ipv6="::1",
                )

        except ImportError:
            pytest.skip("Pydantic not installed")
