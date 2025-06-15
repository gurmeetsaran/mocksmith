"""Binary database types."""

from typing import Any, Optional, Type, Union

from db_types.types.base import DBType


class BINARY(DBType[bytes]):
    """Fixed-length binary type."""

    def __init__(self, length: int):
        super().__init__()
        if length <= 0:
            raise ValueError("BINARY length must be positive")
        self.length = length

    @property
    def sql_type(self) -> str:
        return f"BINARY({self.length})"

    @property
    def python_type(self) -> Type[bytes]:
        return bytes

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (bytes, bytearray, str)):
            raise ValueError(f"Expected binary value, got {type(value).__name__}")

        # Convert to bytes for length check
        if isinstance(value, str):
            byte_value = value.encode("utf-8")
        elif isinstance(value, bytearray):
            byte_value = bytes(value)
        else:
            byte_value = value

        if len(byte_value) > self.length:
            raise ValueError(f"Binary length {len(byte_value)} exceeds maximum {self.length}")

    def _serialize(self, value: Union[bytes, bytearray, str]) -> bytes:
        if isinstance(value, str):
            byte_value = value.encode("utf-8")
        elif isinstance(value, bytearray):
            byte_value = bytes(value)
        else:
            byte_value = value

        # Pad with zeros to match BINARY behavior
        return byte_value.ljust(self.length, b"\x00")

    def _deserialize(self, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value.rstrip(b"\x00")  # Remove padding
        elif isinstance(value, bytearray):
            return bytes(value).rstrip(b"\x00")
        elif isinstance(value, str):
            # Assume hex string or base64
            try:
                return bytes.fromhex(value)
            except ValueError:
                # Try as UTF-8 encoded string
                return value.encode("utf-8")
        else:
            return bytes(value)

    def __repr__(self) -> str:
        return f"BINARY({self.length})"


class VARBINARY(DBType[bytes]):
    """Variable-length binary type."""

    def __init__(self, max_length: int):
        super().__init__()
        if max_length <= 0:
            raise ValueError("VARBINARY max_length must be positive")
        self.max_length = max_length

    @property
    def sql_type(self) -> str:
        return f"VARBINARY({self.max_length})"

    @property
    def python_type(self) -> Type[bytes]:
        return bytes

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (bytes, bytearray, str)):
            raise ValueError(f"Expected binary value, got {type(value).__name__}")

        # Convert to bytes for length check
        if isinstance(value, str):
            byte_value = value.encode("utf-8")
        elif isinstance(value, bytearray):
            byte_value = bytes(value)
        else:
            byte_value = value

        if len(byte_value) > self.max_length:
            raise ValueError(f"Binary length {len(byte_value)} exceeds maximum {self.max_length}")

    def _serialize(self, value: Union[bytes, bytearray, str]) -> bytes:
        if isinstance(value, str):
            return value.encode("utf-8")
        elif isinstance(value, bytearray):
            return bytes(value)
        else:
            return value

    def _deserialize(self, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        elif isinstance(value, bytearray):
            return bytes(value)
        elif isinstance(value, str):
            # Assume hex string or base64
            try:
                return bytes.fromhex(value)
            except ValueError:
                # Try as UTF-8 encoded string
                return value.encode("utf-8")
        else:
            return bytes(value)

    def __repr__(self) -> str:
        return f"VARBINARY({self.max_length})"


class BLOB(DBType[bytes]):
    """Binary Large Object type."""

    def __init__(self, max_length: Optional[int] = None):
        super().__init__()
        self.max_length = max_length

    @property
    def sql_type(self) -> str:
        return "BLOB"

    @property
    def python_type(self) -> Type[bytes]:
        return bytes

    def validate(self, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, (bytes, bytearray, str)):
            raise ValueError(f"Expected binary value, got {type(value).__name__}")

        if self.max_length:
            # Convert to bytes for length check
            if isinstance(value, str):
                byte_value = value.encode("utf-8")
            elif isinstance(value, bytearray):
                byte_value = bytes(value)
            else:
                byte_value = value

            if len(byte_value) > self.max_length:
                raise ValueError(f"BLOB length {len(byte_value)} exceeds maximum {self.max_length}")

    def _serialize(self, value: Union[bytes, bytearray, str]) -> bytes:
        if isinstance(value, str):
            return value.encode("utf-8")
        elif isinstance(value, bytearray):
            return bytes(value)
        else:
            return value

    def _deserialize(self, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        elif isinstance(value, bytearray):
            return bytes(value)
        elif isinstance(value, str):
            # Assume hex string or base64
            try:
                return bytes.fromhex(value)
            except ValueError:
                # Try as UTF-8 encoded string
                return value.encode("utf-8")
        else:
            return bytes(value)

    def __repr__(self) -> str:
        if self.max_length:
            return f"BLOB(max_length={self.max_length})"
        return "BLOB()"
