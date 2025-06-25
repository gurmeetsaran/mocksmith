"""Comprehensive dataclass example demonstrating all python-db-types features.

This example shows:
- Basic usage with all data types
- Constrained numeric types
- Clean API for constraints
- Validation and error handling
- SQL serialization
- Optional vs required fields
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Optional

from mocksmith import (
    BigInt,
    Binary,
    Blob,
    Boolean,
    Char,
    Date,
    DateTime,
    DecimalType,
    Double,
    Float,
    Integer,
    Money,
    NonNegativeInteger,
    NonPositiveInteger,
    PositiveInteger,
    Real,
    SmallInt,
    Text,
    Time,
    Timestamp,
    TinyInt,
    VarBinary,
    Varchar,
)
from mocksmith.dataclass_integration import validate_dataclass

# ============================================================================
# EXAMPLE 1: Comprehensive Employee Model
# ============================================================================


@validate_dataclass
@dataclass
class Employee:
    """Demonstrates all basic data types and features."""

    # === REQUIRED FIELDS (no defaults) ===
    employee_id: Integer()
    email: Varchar(255)
    username: Varchar(30)

    # === OPTIONAL FIELDS (using Optional[Type]) ===
    first_name: Optional[Varchar(50)] = None
    last_name: Optional[Varchar(50)] = None
    middle_name: Optional[Varchar(50)] = None
    bio: Optional[Text(max_length=1000)] = None
    phone: Optional[Varchar(20)] = None

    # === FIELDS WITH DEFAULTS ===
    department: Varchar(50) = "Engineering"
    employee_code: Char(10) = "EMP0000000"  # Fixed-length, padded
    is_active: Boolean() = True
    is_manager: Boolean() = False

    # === NUMERIC FIELDS ===
    salary: Money() = Decimal("0.00")  # Alias for DECIMAL(19,4)
    bonus_percentage: DecimalType(5, 2) = Decimal("0.00")  # Max 999.99%
    years_experience: SmallInt() = 0  # 16-bit: -32768 to 32767
    vacation_days: Integer() = 20  # 32-bit integer
    employee_number: BigInt() = 0  # 64-bit integer

    # === DATE/TIME FIELDS ===
    hire_date: Date() = None
    birth_date: Optional[Date()] = None
    last_login: Optional[Timestamp()] = None  # With timezone
    last_review: Optional[DateTime()] = None  # Without timezone
    work_start_time: Time(precision=0) = time(9, 0, 0)  # No fractional seconds

    # === BINARY DATA ===
    avatar: Optional[Blob(max_length=1048576)] = None  # 1MB max
    employee_badge: Optional[Binary(16)] = None  # Fixed 16 bytes
    fingerprint: Optional[VarBinary(512)] = None  # Variable up to 512 bytes

    # === FLOATING POINT FIELDS ===
    performance_score: Float() = 0.0  # FLOAT type
    efficiency_rating: Real() = 0.0  # REAL type (single precision in SQL)
    accuracy_percentage: Double() = 0.0  # DOUBLE type

    def __post_init__(self):
        """Set default hire_date if not provided."""
        if self.hire_date is None:
            self.hire_date = datetime.now(timezone.utc).date()


# ============================================================================
# EXAMPLE 2: Product Inventory with Constrained Types
# ============================================================================


@validate_dataclass
@dataclass
class ProductInventory:
    """Demonstrates constrained numeric types."""

    # IDs must be positive
    product_id: PositiveInteger()
    warehouse_id: Integer(positive=True)  # Alternative syntax

    # Quantities with constraints
    quantity_on_hand: NonNegativeInteger()  # >= 0
    reorder_level: Integer(min_value=0, max_value=10000)
    min_order_quantity: Integer(min_value=1, max_value=1000)

    # Percentage constraints
    discount_percentage: Integer(min_value=0, max_value=100, multiple_of=5)

    # Financial constraints
    unit_cost_cents: NonNegativeInteger()  # Price in cents
    max_discount_amount: Integer(min_value=0, max_value=100000)  # $0 to $1000

    # Fields with defaults must come after required fields
    tax_rate_percentage: DecimalType(4, 2) = Decimal("0.00")  # 0.00 to 99.99


# ============================================================================
# EXAMPLE 3: Game Character with Varied Constraints
# ============================================================================


@validate_dataclass
@dataclass
class GameCharacter:
    """Demonstrates complex constraint scenarios."""

    # Basic info with constraints
    character_id: PositiveInteger()
    player_id: BigInt(positive=True)

    # Level and experience
    level: Integer(min_value=1, max_value=100)
    experience_points: NonNegativeInteger()
    skill_points: NonNegativeInteger()

    # Stats that can go negative (debuffs)
    health: Integer(min_value=-100, max_value=9999)
    mana: NonNegativeInteger()
    stamina: Integer(min_value=0, max_value=100)

    # Modifiers
    strength_modifier: Integer(min_value=-10, max_value=10)
    defense_modifier: Integer(min_value=-10, max_value=10)
    speed_modifier: SmallInt(min_value=-5, max_value=5)

    # Currency (can have debt)
    gold: NonNegativeInteger()
    debt: NonPositiveInteger()  # <= 0
    bank_balance: Integer()  # Can be positive or negative

    # Reputation system
    reputation: Integer(min_value=-1000, max_value=1000, multiple_of=10)
    honor_points: NonNegativeInteger()
    infamy_points: NonNegativeInteger()


# ============================================================================
# EXAMPLE 4: System Configuration with TinyInt
# ============================================================================


@validate_dataclass
@dataclass
class SystemConfig:
    """Demonstrates TINYINT usage for small bounded values."""

    config_id: PositiveInteger()
    server_id: SmallInt(positive=True)

    # Log levels (0-5)
    log_level: TinyInt(min_value=0, max_value=5)  # 0=DEBUG, 5=CRITICAL

    # System limits
    max_retries: TinyInt(min_value=0, max_value=10)
    thread_pool_size: TinyInt(min_value=1, max_value=100)
    connection_pool_size: TinyInt(min_value=1, max_value=50)

    # Percentage values (perfect for TINYINT)
    cpu_threshold_percent: TinyInt(min_value=0, max_value=100)
    memory_threshold_percent: TinyInt(min_value=0, max_value=100)
    disk_threshold_percent: TinyInt(min_value=0, max_value=100)

    # Priority and quality settings
    priority: TinyInt(min_value=-5, max_value=5)  # -5=lowest, 5=highest
    quality_level: TinyInt(min_value=1, max_value=10)
    compression_level: TinyInt(min_value=0, max_value=9)


# ============================================================================
# EXAMPLE 5: Scientific Measurement Data
# ============================================================================


@validate_dataclass
@dataclass
class ScientificMeasurement:
    """Demonstrates floating-point types and precision."""

    measurement_id: BigInt(positive=True)
    experiment_id: Integer(positive=True)

    # Different float types
    temperature_celsius: Float()  # General floating point
    pressure_pascals: Real()  # Single precision (REAL SQL type)
    energy_joules: Double()  # Double precision

    # High precision decimals for exact values
    weight_grams: DecimalType(10, 6)  # Up to 9999.999999g
    volume_liters: DecimalType(8, 4)  # Up to 9999.9999L
    concentration_molar: DecimalType(6, 4)  # Up to 99.9999M

    # Measurement metadata
    measurement_time: Timestamp(precision=6)  # Microsecond precision
    duration_seconds: DecimalType(10, 6)
    uncertainty_percentage: Float() = 0.0

    # Validation flags
    is_calibrated: Boolean() = False
    is_validated: Boolean() = False
    passed_qc: Optional[Boolean()] = None


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================


def demonstrate_basic_usage():
    """Show basic dataclass usage with python-db-types."""
    print("=" * 80)
    print("BASIC USAGE - Employee Model".center(80))
    print("=" * 80)

    # Create with minimal fields
    emp1 = Employee(employee_id=1, email="john.doe@company.com", username="jdoe")
    print(f"\n1. Minimal employee: {emp1.username} ({emp1.email})")
    print(f"   Department: {emp1.department} (default)")
    print(f"   Hire date: {emp1.hire_date} (auto-set)")

    # Create with full data
    emp2 = Employee(
        employee_id=2,
        email="jane.smith@company.com",
        username="jsmith",
        first_name="Jane",
        last_name="Smith",
        salary=Decimal("95000.00"),
        bonus_percentage=Decimal("15.50"),
        is_manager=True,
        hire_date=date(2020, 1, 15),
        work_start_time=time(8, 30, 0),
    )
    print(f"\n2. Full employee: {emp2.first_name} {emp2.last_name}")
    print(f"   Salary: ${emp2.salary}")
    print(f"   Bonus: {emp2.bonus_percentage}%")

    # Type conversions
    emp3 = Employee(
        employee_id=3,
        email="auto@company.com",
        username="auto",
        is_active="yes",  # String → Boolean
        salary="75000.00",  # String → Decimal
        hire_date="2023-06-15",  # String → Date
    )
    print("\n3. Type conversions:")
    print(f"   'yes' → {emp3.is_active} (Boolean)")
    print(f"   '75000.00' → ${emp3.salary} (Decimal)")
    print(f"   '2023-06-15' → {emp3.hire_date} (Date)")


def demonstrate_constraints():
    """Show constraint validation."""
    print("\n" + "=" * 80)
    print("CONSTRAINT VALIDATION".center(80))
    print("=" * 80)

    # Valid inventory
    print("\n1. Valid product inventory:")
    inv = ProductInventory(
        product_id=123,
        warehouse_id=1,
        quantity_on_hand=50,
        reorder_level=10,
        min_order_quantity=5,
        discount_percentage=15,  # Valid: multiple of 5
        unit_cost_cents=2999,  # $29.99
        max_discount_amount=500,  # $5.00
    )
    print(f"   Product {inv.product_id}: {inv.quantity_on_hand} units on hand")
    print(f"   Reorder at: {inv.reorder_level} units")
    print(f"   Discount: {inv.discount_percentage}%")

    # Constraint violations
    print("\n2. Constraint violations:")

    try:
        ProductInventory(
            product_id=0,  # Invalid: must be positive
            warehouse_id=1,
            quantity_on_hand=0,
            reorder_level=0,
            min_order_quantity=1,
            discount_percentage=0,
            unit_cost_cents=0,
            max_discount_amount=0,
        )
    except ValueError as e:
        print(f"   ✗ Product ID: {e}")

    try:
        ProductInventory(
            product_id=1,
            warehouse_id=1,
            quantity_on_hand=-5,  # Invalid: must be non-negative
            reorder_level=0,
            min_order_quantity=1,
            discount_percentage=0,
            unit_cost_cents=0,
            max_discount_amount=0,
        )
    except ValueError as e:
        print(f"   ✗ Quantity: {e}")

    try:
        ProductInventory(
            product_id=1,
            warehouse_id=1,
            quantity_on_hand=0,
            reorder_level=0,
            min_order_quantity=1,
            discount_percentage=17,  # Invalid: not multiple of 5
            unit_cost_cents=0,
            max_discount_amount=0,
        )
    except ValueError as e:
        print(f"   ✗ Discount: {e}")


def demonstrate_game_character():
    """Show complex constraint scenarios."""
    print("\n" + "=" * 80)
    print("COMPLEX CONSTRAINTS - Game Character".center(80))
    print("=" * 80)

    # Create character
    char = GameCharacter(
        character_id=42,
        player_id=1001,
        level=15,
        experience_points=25000,
        skill_points=10,
        health=85,
        mana=50,
        stamina=75,
        strength_modifier=3,
        defense_modifier=-1,
        speed_modifier=2,
        gold=1250,
        debt=-100,  # Owes 100 gold
        bank_balance=5000,
        reputation=200,  # Multiple of 10
        honor_points=150,
        infamy_points=20,
    )

    print(f"\nCharacter {char.character_id} (Level {char.level}):")
    print(f"  Health: {char.health} | Mana: {char.mana} | Stamina: {char.stamina}")
    print(
        f"  Modifiers - STR: {char.strength_modifier:+d}, "
        + f"DEF: {char.defense_modifier:+d}, SPD: {char.speed_modifier:+d}"
    )
    print(f"  Finances - Gold: {char.gold}, Debt: {char.debt}, Bank: {char.bank_balance}")
    print(
        f"  Reputation: {char.reputation} "
        + f"(Honor: {char.honor_points}, Infamy: {char.infamy_points})"
    )


def demonstrate_tinyint():
    """Show TINYINT usage for small values."""
    print("\n" + "=" * 80)
    print("TINYINT USAGE - System Configuration".center(80))
    print("=" * 80)

    config = SystemConfig(
        config_id=1,
        server_id=10,
        log_level=2,  # INFO
        max_retries=3,
        thread_pool_size=8,
        connection_pool_size=20,
        cpu_threshold_percent=80,
        memory_threshold_percent=90,
        disk_threshold_percent=85,
        priority=0,  # Normal
        quality_level=7,
        compression_level=6,
    )

    print(f"\nSystem Configuration #{config.config_id}:")
    print(f"  Server: {config.server_id}")
    print(f"  Log Level: {config.log_level} (0=DEBUG, 5=CRITICAL)")
    print(
        f"  Pools - Threads: {config.thread_pool_size}, "
        + f"Connections: {config.connection_pool_size}"
    )
    print(
        f"  Thresholds - CPU: {config.cpu_threshold_percent}%, "
        + f"Memory: {config.memory_threshold_percent}%, "
        + f"Disk: {config.disk_threshold_percent}%"
    )
    print(
        f"  Settings - Priority: {config.priority:+d}, "
        + f"Quality: {config.quality_level}/10, "
        + f"Compression: {config.compression_level}/9"
    )

    # Show TINYINT range
    print("\n  TINYINT ranges:")
    print("    8-bit signed: -128 to 127")
    print("    Perfect for: percentages, small counts, flags, levels")


def demonstrate_sql_serialization():
    """Show SQL serialization features."""
    print("\n" + "=" * 80)
    print("SQL SERIALIZATION".center(80))
    print("=" * 80)

    # Create a measurement
    measurement = ScientificMeasurement(
        measurement_id=1001,
        experiment_id=42,
        temperature_celsius=23.456,
        pressure_pascals=101325.0,
        energy_joules=1234.5678,
        weight_grams=Decimal("15.123456"),
        volume_liters=Decimal("2.5000"),
        concentration_molar=Decimal("0.1234"),
        measurement_time=datetime.now(timezone.utc),
        duration_seconds=Decimal("3600.000000"),
        uncertainty_percentage=0.05,
        is_calibrated=True,
        is_validated=True,
        passed_qc=True,
    )

    # Get SQL representation
    sql_data = measurement.to_sql_dict()
    print("\nSQL representation (selected fields):")
    for field in [
        "measurement_id",
        "temperature_celsius",
        "weight_grams",
        "measurement_time",
        "is_calibrated",
    ]:
        print(f"  {field}: {sql_data[field]!r}")

    # Get database types
    db_types = measurement.get_db_types()
    print("\nDatabase type information:")
    print(f"  temperature_celsius: {db_types['temperature_celsius'].sql_type}")
    print(f"  pressure_pascals: {db_types['pressure_pascals'].sql_type}")
    print(f"  weight_grams: {db_types['weight_grams'].sql_type}")
    print(f"  measurement_time: {db_types['measurement_time'].sql_type}")


def demonstrate_validation_errors():
    """Show various validation error scenarios."""
    print("\n" + "=" * 80)
    print("VALIDATION ERROR EXAMPLES".center(80))
    print("=" * 80)

    print("\n1. String length validation:")
    try:
        Employee(
            employee_id=1,
            email="test@company.com",
            username="this_username_is_way_too_long_for_varchar_30",
        )
    except ValueError as e:
        print(f"   ✗ {e}")

    print("\n2. Numeric range validation:")
    try:
        Employee(
            employee_id=1,
            email="test@company.com",
            username="test",
            years_experience=40000,  # Too big for SMALLINT
        )
    except ValueError as e:
        print(f"   ✗ {e}")

    print("\n3. Decimal precision validation:")
    try:
        Employee(
            employee_id=1,
            email="test@company.com",
            username="test",
            bonus_percentage=Decimal("1234.567"),  # Too many digits
        )
    except ValueError as e:
        print(f"   ✗ {e}")

    print("\n4. TINYINT range validation:")
    try:
        SystemConfig(
            config_id=1,
            server_id=1,
            log_level=10,  # Max is 5
            max_retries=3,
            thread_pool_size=8,
            connection_pool_size=20,
            cpu_threshold_percent=80,
            memory_threshold_percent=90,
            disk_threshold_percent=85,
            priority=0,
            quality_level=7,
            compression_level=6,
        )
    except ValueError as e:
        print(f"   ✗ {e}")

    print("\n5. Constraint validation:")
    try:
        GameCharacter(
            character_id=1,
            player_id=1,
            level=150,  # Max is 100
            experience_points=0,
            skill_points=0,
            health=100,
            mana=0,
            stamina=0,
            strength_modifier=0,
            defense_modifier=0,
            speed_modifier=0,
            gold=0,
            debt=0,
            bank_balance=0,
            reputation=0,
            honor_points=0,
            infamy_points=0,
        )
    except ValueError as e:
        print(f"   ✗ {e}")


def demonstrate_pydantic_types_limitations():
    """Show limitations of using Pydantic types in dataclasses."""
    print("\n" + "=" * 80)
    print("PYDANTIC TYPES IN DATACLASSES - LIMITATIONS".center(80))
    print("=" * 80)

    print("\nIMPORTANT: Pydantic types in dataclasses work as type hints only!")
    print("No automatic validation occurs.\n")

    try:
        from pydantic import EmailStr, HttpUrl, conint

        @dataclass
        class ServerConfig:
            """Dataclass using Pydantic types as annotations."""

            hostname: str
            port: conint(ge=1, le=65535)
            admin_email: EmailStr
            api_url: HttpUrl

        # This creates an instance WITHOUT validation
        server = ServerConfig(
            hostname="api.example.com",
            port=99999,  # Out of range! But no error
            admin_email="invalid-email",  # Invalid! But no error
            api_url="not-a-url",  # Invalid! But no error
        )

        print("Example: Created dataclass with INVALID data:")
        print(f"  Port: {server.port} (should be 1-65535)")
        print(f"  Email: {server.admin_email} (invalid format)")
        print(f"  URL: {server.api_url} (invalid URL)")
        print("\nNote: All invalid values were accepted!")

        print("\nRECOMMENDATION:")
        print("• For validation with Pydantic types, use Pydantic's BaseModel")
        print("• For dataclasses, use mocksmith's types: Varchar(50), Integer(), etc.")
        print("• mocksmith types provide validation via @validate_dataclass")

    except ImportError:
        print("(Pydantic not installed - skipping this demonstration)")


def main():
    """Run all demonstrations."""
    demonstrate_basic_usage()
    demonstrate_constraints()
    demonstrate_game_character()
    demonstrate_tinyint()
    demonstrate_sql_serialization()
    demonstrate_validation_errors()
    demonstrate_pydantic_types_limitations()

    print("\n" + "=" * 80)
    print("KEY FEATURES".center(80))
    print("=" * 80)
    print(
        """
✓ Clean syntax: Varchar(50) instead of Annotated[str, VARCHAR(50)]
✓ Works exactly like Pydantic: Optional[Type] = None for optional fields
✓ Automatic type conversion: strings → dates, decimals, booleans
✓ Comprehensive validation: length, range, precision, custom constraints
✓ SQL serialization: to_sql_dict() for database operations
✓ All standard SQL types: INTEGER, VARCHAR, DECIMAL, TIMESTAMP, etc.
✓ Constraint types: PositiveInteger(), NonNegativeInteger(), etc.
✓ Flexible constraints: min_value, max_value, multiple_of
✓ TINYINT support: Perfect for small bounded values (8-bit)
✓ REAL vs FLOAT: Proper SQL type generation
"""
    )


if __name__ == "__main__":
    main()
