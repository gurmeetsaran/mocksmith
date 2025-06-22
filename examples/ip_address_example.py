"""Example demonstrating IP address types in mocksmith.

This example shows how to use IPAddress, IPv4Address, and IPv6Address types
for network-related data validation and mock generation.
"""

from dataclasses import dataclass
from typing import Annotated, Optional

from mocksmith import mockable
from mocksmith.specialized import IPAddress, IPv4Address, IPv6Address


@mockable
@dataclass
class NetworkInterface:
    """Network interface configuration."""

    name: str
    ipv4_address: Annotated[str, IPv4Address()]
    ipv6_address: Optional[Annotated[str, IPv6Address()]] = None
    gateway: Optional[Annotated[str, IPv4Address()]] = None


@mockable
@dataclass
class Server:
    """Server with network configuration."""

    hostname: str
    management_ip: Annotated[str, IPAddress()]  # Can be IPv4 or IPv6
    primary_ipv4: Annotated[str, IPv4Address()]
    primary_ipv6: Optional[Annotated[str, IPv6Address()]] = None
    backup_ip: Optional[Annotated[str, IPAddress()]] = None


def main():
    """Demonstrate IP address types."""
    print("=== IP Address Types Example ===\n")

    # Example 1: Direct validation
    print("1. Direct IP validation:")
    ip_validator = IPAddress()

    # Valid IPs
    valid_ips = [
        ("192.168.1.1", "IPv4"),
        ("10.0.0.1", "IPv4"),
        ("2001:db8::1", "IPv6"),
        ("::1", "IPv6 loopback"),
    ]

    for ip, desc in valid_ips:
        try:
            ip_validator.validate(ip)
            print(f"  ✓ {ip} ({desc}) - Valid")
        except ValueError as e:
            print(f"  ✗ {ip} ({desc}) - {e}")

    # Invalid IPs
    print("\n  Testing invalid IPs:")
    invalid_ips = ["256.256.256.256", "not.an.ip", "192.168.1"]
    for ip in invalid_ips:
        try:
            ip_validator.validate(ip)
            print(f"  ✗ {ip} - Should have failed!")
        except ValueError:
            print(f"  ✓ {ip} - Correctly rejected")

    # Example 2: Mock generation
    print("\n2. Mock IP generation:")
    for i in range(5):
        server = Server.mock()
        print(f"\n  Server {i + 1}:")
        print(f"    Hostname: {server.hostname}")
        print(f"    Management IP: {server.management_ip}")
        print(f"    Primary IPv4: {server.primary_ipv4}")
        print(f"    Primary IPv6: {server.primary_ipv6}")
        print(f"    Backup IP: {server.backup_ip}")

    # Example 3: Builder pattern
    print("\n3. Using builder pattern:")
    custom_server = (
        Server.mock_builder()
        .with_hostname("web-server-01")
        .with_management_ip("10.10.10.100")
        .build()
    )

    print(f"  Custom server: {custom_server.hostname}")
    print(f"  Management IP: {custom_server.management_ip}")

    # Example 4: Specific IP type usage
    print("\n4. IPv4 vs IPv6 specific types:")

    # IPv4 only
    ipv4_only = IPv4Address()
    print("\n  IPv4 only validation:")
    try:
        ipv4_only.validate("192.168.1.1")
        print("    ✓ 192.168.1.1 - Valid IPv4")
    except ValueError as e:
        print(f"    ✗ 192.168.1.1 - {e}")

    try:
        ipv4_only.validate("2001:db8::1")
        print("    ✗ 2001:db8::1 - Should have failed (IPv6)!")
    except ValueError:
        print("    ✓ 2001:db8::1 - Correctly rejected (not IPv4)")

    # IPv6 only
    ipv6_only = IPv6Address()
    print("\n  IPv6 only validation:")
    try:
        ipv6_only.validate("2001:db8::1")
        print("    ✓ 2001:db8::1 - Valid IPv6")
    except ValueError as e:
        print(f"    ✗ 2001:db8::1 - {e}")

    try:
        ipv6_only.validate("192.168.1.1")
        print("    ✗ 192.168.1.1 - Should have failed (IPv4)!")
    except ValueError:
        print("    ✓ 192.168.1.1 - Correctly rejected (not IPv6)")

    # Example 5: SQL type representation
    print("\n5. SQL type representation:")
    print(f"  IPAddress -> {IPAddress().sql_type}")
    print(f"  IPv4Address -> {IPv4Address().sql_type}")
    print(f"  IPv6Address -> {IPv6Address().sql_type}")


# Pydantic example
try:
    from typing import Annotated

    from pydantic import BaseModel

    from mocksmith.pydantic_v2 import DBTypeValidator  # pyright: ignore[reportMissingImports]

    @mockable
    class NetworkConfig(BaseModel):
        """Network configuration using Pydantic."""

        interface_name: str
        ip_address: Annotated[str, DBTypeValidator(IPAddress())]
        subnet_mask: Annotated[str, DBTypeValidator(IPv4Address())]
        dns_servers: list[Annotated[str, DBTypeValidator(IPv4Address())]]
        ipv6_enabled: bool = False
        ipv6_address: Optional[Annotated[str, DBTypeValidator(IPv6Address())]] = None

    def pydantic_example():
        """Show IP address types with Pydantic."""
        print("\n\n=== Pydantic IP Address Example ===")

        # Generate mock config
        config = NetworkConfig.mock()
        print("\nGenerated network config:")
        print(f"  Interface: {config.interface_name}")
        print(f"  IP: {config.ip_address}")
        print(f"  Subnet mask: {config.subnet_mask}")
        print(f"  DNS servers: {config.dns_servers}")
        print(f"  IPv6 enabled: {config.ipv6_enabled}")
        print(f"  IPv6 address: {config.ipv6_address}")

        # Validation example
        print("\nValidation example:")
        try:
            NetworkConfig(
                interface_name="eth0",
                ip_address="invalid.ip.address",
                subnet_mask="255.255.255.0",
                dns_servers=["8.8.8.8", "8.8.4.4"],
            )
            print("  ERROR: Should have failed validation!")
        except ValueError as e:
            print(f"  ✓ Validation correctly failed: {type(e).__name__}")

    # Run Pydantic example if available
    pydantic_example()

except ImportError:
    print("\n(Pydantic not installed, skipping Pydantic example)")


if __name__ == "__main__":
    main()
