"""Binary types with V3 pattern - extends Python bytes directly."""

from typing import Any, ClassVar, Optional

try:
    from pydantic import GetCoreSchemaHandler  # type: ignore
    from pydantic_core import PydanticCustomError, core_schema  # type: ignore

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    GetCoreSchemaHandler = Any
    core_schema = None
    PydanticCustomError = ValueError


class _BaseBinary(bytes):
    """Base class for all binary types."""

    # To be defined by subclasses
    SQL_TYPE: ClassVar[str]
    _length: Optional[int] = None  # For BINARY
    _max_length: Optional[int] = None  # For VARBINARY/BLOB

    def __new__(cls, value: Any) -> "_BaseBinary":
        """Create new binary with validation."""
        if value is None:
            raise ValueError(f"{cls.SQL_TYPE} cannot be None")

        # Convert to bytes
        if isinstance(value, bytes):
            byte_value = value
        elif isinstance(value, bytearray):
            byte_value = bytes(value)
        elif isinstance(value, str):
            # Try hex string first
            try:
                # Remove common hex prefixes
                hex_str = value
                if hex_str.startswith(("0x", "0X")):
                    hex_str = hex_str[2:]
                byte_value = bytes.fromhex(hex_str)
            except ValueError:
                # Fall back to UTF-8 encoding
                byte_value = value.encode("utf-8")
        elif isinstance(value, int):
            # Convert int to bytes (big-endian)
            byte_value = value.to_bytes((value.bit_length() + 7) // 8, "big")
        else:
            try:
                byte_value = bytes(value)
            except Exception as e:
                raise ValueError(f"Cannot convert {type(value).__name__} to bytes") from e

        # Check length constraints
        if cls._length is not None:
            # BINARY - fixed length, pad or truncate
            if len(byte_value) > cls._length:
                raise ValueError(
                    f"Binary data length {len(byte_value)} exceeds " f"fixed length {cls._length}"
                )
            # Pad with zeros to match fixed length
            byte_value = byte_value.ljust(cls._length, b"\x00")
        elif cls._max_length is not None:
            # VARBINARY/BLOB - variable length with max
            if len(byte_value) > cls._max_length:
                raise ValueError(
                    f"Binary data length {len(byte_value)} exceeds "
                    f"maximum length {cls._max_length}"
                )

        return super().__new__(cls, byte_value)

    def __repr__(self) -> str:
        """Developer representation."""
        hex_str = self.hex()
        if len(hex_str) > 20:
            hex_str = hex_str[:20] + "..."
        return f"{self.__class__.__name__}(0x{hex_str})"

    @property
    def sql_type(self) -> str:
        """Return SQL type for compatibility."""
        if self._length is not None:
            return f"{self.SQL_TYPE}({self._length})"
        elif self._max_length is not None:
            return f"{self.SQL_TYPE}({self._max_length})"
        return self.SQL_TYPE

    def serialize(self) -> bytes:
        """Serialize for SQL."""
        return bytes(self)

    @classmethod
    def validate(cls, value: Any) -> bytes:
        """Validate a value without creating an instance (compatibility method)."""
        instance = cls(value)
        return bytes(instance)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        """Define Pydantic validation schema."""
        if not PYDANTIC_AVAILABLE:
            return None

        def validate_binary(value: Any) -> bytes:
            """Validate and convert to bytes."""
            try:
                instance = cls(value)
                return bytes(instance)
            except ValueError as e:
                raise PydanticCustomError(f"{cls.SQL_TYPE.lower()}_type", str(e)) from e

        return core_schema.no_info_after_validator_function(  # type: ignore
            validate_binary,
            core_schema.union_schema(  # type: ignore
                [  # type: ignore
                    core_schema.bytes_schema(),  # type: ignore
                    core_schema.str_schema(),  # type: ignore
                ]
            ),
        )

    @classmethod
    def mock(cls) -> bytes:
        """Generate mock binary data."""
        try:
            from faker import Faker  # type: ignore

            fake = Faker()

            if cls._length is not None:
                # Fixed length
                return fake.binary(length=cls._length)
            elif cls._max_length is not None:
                # Variable length up to max
                length = fake.random_int(min=1, max=min(cls._max_length, 100))
                return fake.binary(length=length)
            else:
                # BLOB without max - reasonable size
                length = fake.random_int(min=100, max=1000)
                return fake.binary(length=length)
        except ImportError:
            raise ImportError("faker library is required for mock generation") from None


class BINARY(_BaseBinary):
    """Fixed-length binary type."""

    SQL_TYPE = "BINARY"

    def __new__(cls, value: Any, *, _create_type: bool = False):  # type: ignore
        """Create new BINARY instance or type class."""
        if _create_type:
            # This is a type creation call, return the value (which is a class)
            return value
        return super().__new__(cls, value)


class VARBINARY(_BaseBinary):
    """Variable-length binary type."""

    SQL_TYPE = "VARBINARY"

    def __new__(cls, value: Any, *, _create_type: bool = False):  # type: ignore
        """Create new VARBINARY instance or type class."""
        if _create_type:
            # This is a type creation call, return the value (which is a class)
            return value
        return super().__new__(cls, value)


class BLOB(_BaseBinary):
    """Binary Large Object type."""

    SQL_TYPE = "BLOB"

    def __new__(cls, value: Any, *, _create_type: bool = False):  # type: ignore
        """Create new BLOB instance or type class."""
        if _create_type:
            # This is a type creation call, return the value (which is a class)
            return value
        return super().__new__(cls, value)


# Factory functions
def Binary(length: int) -> type:  # noqa: N802
    """Create a fixed-length binary type.

    Args:
        length: Fixed length in bytes

    Example:
        class File(BaseModel):
            hash: Binary(32)  # MD5 hash
            signature: Binary(64)
    """
    if length <= 0:
        raise ValueError("BINARY length must be positive")

    class ConstrainedBinary(BINARY):
        _length = length
        SQL_TYPE = "BINARY"

    # Use the special _create_type flag to return the class
    return BINARY(ConstrainedBinary, _create_type=True)  # type: ignore


def VarBinary(max_length: int) -> type:  # noqa: N802
    """Create a variable-length binary type.

    Args:
        max_length: Maximum length in bytes

    Example:
        class Document(BaseModel):
            thumbnail: VarBinary(1024)
            preview: VarBinary(10240)
    """
    if max_length <= 0:
        raise ValueError("VARBINARY max_length must be positive")

    class ConstrainedVarBinary(VARBINARY):
        _max_length = max_length
        SQL_TYPE = "VARBINARY"

    return VARBINARY(ConstrainedVarBinary, _create_type=True)  # type: ignore


def Blob(max_length: Optional[int] = None) -> type:  # noqa: N802
    """Create a BLOB type.

    Args:
        max_length: Optional maximum length in bytes

    Example:
        class Media(BaseModel):
            data: Blob()
            thumbnail: Blob(max_length=65536)  # 64KB max
    """
    if max_length is not None and max_length <= 0:
        raise ValueError("BLOB max_length must be positive if specified")

    class ConstrainedBlob(BLOB):
        _max_length = max_length
        SQL_TYPE = "BLOB"

    return BLOB(ConstrainedBlob, _create_type=True)  # type: ignore
