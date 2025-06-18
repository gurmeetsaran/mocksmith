"""Comprehensive Pydantic example demonstrating all python-db-types features.

This example shows:
- Basic usage with all data types
- Constrained numeric types
- Clean API for constraints
- Validation and error handling
- JSON serialization
- Field validators
- Optional vs required fields
"""

from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

from db_types import Numeric  # Alias for DecimalType
from db_types import (
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

# ============================================================================
# EXAMPLE 1: Comprehensive Employee Model
# ============================================================================


class Employee(BaseModel):
    """Demonstrates all basic data types and features with Pydantic."""

    # === REQUIRED FIELDS (no defaults) ===
    employee_id: Integer()
    email: Varchar(255)
    username: Varchar(30)

    # === OPTIONAL FIELDS (using Optional[Type] = None) ===
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

    # Using Numeric alias (same as DecimalType)
    tax_rate: Numeric(4, 2) = Decimal("0.00")  # 0.00 to 99.99

    # === DATE/TIME FIELDS ===
    hire_date: Date() = Field(default_factory=date.today)
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

    # === CUSTOM VALIDATORS ===
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Ensure email is lowercase and from company domain."""
        v = v.lower()
        if "@" not in v:
            raise ValueError("Invalid email format")
        if not v.endswith("@company.com"):
            raise ValueError("Email must be @company.com domain")
        return v

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v: Decimal) -> Decimal:
        """Ensure salary is non-negative."""
        if v < 0:
            raise ValueError("Salary cannot be negative")
        if v > Decimal("1000000"):
            raise ValueError("Salary exceeds maximum allowed")
        return v

    # === COMPUTED PROPERTIES ===
    @property
    def full_name(self) -> str:
        """Computed full name from parts."""
        parts = [n for n in [self.first_name, self.middle_name, self.last_name] if n]
        return " ".join(parts) if parts else self.username

    @property
    def annual_compensation(self) -> Decimal:
        """Total compensation including bonus."""
        bonus = self.salary * (self.bonus_percentage / 100)
        return self.salary + bonus

    # === PYDANTIC CONFIG ===
    model_config = {
        "validate_assignment": True,  # Validate on field assignment
        "json_encoders": {
            Decimal: str,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
            time: lambda v: v.isoformat(),
            bytes: lambda v: v.hex() if v else None,
        },
    }


# ============================================================================
# EXAMPLE 2: E-commerce Order with Constraints
# ============================================================================


class OrderItem(BaseModel):
    """Demonstrates constrained numeric types in e-commerce context."""

    # IDs must be positive
    order_id: BigInt(positive=True)
    product_id: PositiveInteger()
    customer_id: Integer(positive=True)

    # Quantities with constraints
    quantity: Integer(min_value=1, max_value=9999)
    unit_price_cents: NonNegativeInteger()  # Price in cents
    discount_amount_cents: NonNegativeInteger()

    # Percentage constraints
    discount_percentage: Integer(min_value=0, max_value=100, multiple_of=5)
    tax_rate_basis_points: Integer(min_value=0, max_value=10000, multiple_of=25)  # 0.25% increments

    # Status and metadata
    status: Varchar(20) = "pending"
    notes: Optional[Text(max_length=500)] = None
    created_at: Timestamp() = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Additional quantity validation."""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

    @property
    def subtotal_cents(self) -> int:
        """Calculate subtotal in cents."""
        return self.quantity * self.unit_price_cents

    @property
    def total_cents(self) -> int:
        """Calculate total after discount and tax."""
        subtotal = self.subtotal_cents
        after_discount = subtotal - self.discount_amount_cents
        tax = int(after_discount * self.tax_rate_basis_points / 10000)
        return after_discount + tax


# ============================================================================
# EXAMPLE 3: User Account with Profile
# ============================================================================


class UserAccount(BaseModel):
    """Demonstrates user account with various constraints."""

    # User identification
    user_id: PositiveInteger()
    username: Varchar(30)
    email: Varchar(255)

    # Age and demographic constraints
    age: Integer(min_value=13, max_value=120)
    years_active: NonNegativeInteger()

    # Financial information
    credit_score: Integer(min_value=300, max_value=850)
    credit_balance_cents: NonNegativeInteger()  # In cents
    loyalty_points: NonNegativeInteger()
    cashback_percentage: DecimalType(3, 2) = Decimal("1.00")  # 0.00 to 9.99%

    # Preferences with TINYINT
    notification_hour: TinyInt(min_value=0, max_value=23)  # 0-23 hour
    timezone_offset: SmallInt(min_value=-12, max_value=14)  # GMT offset
    language_preference: Char(2) = "en"  # ISO 639-1

    # Account status
    is_verified: Boolean() = False
    is_premium: Boolean() = False
    account_type: Varchar(20) = "standard"

    # Dates
    registered_at: Timestamp() = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[Timestamp()] = None
    subscription_expires: Optional[Date()] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Ensure username is alphanumeric."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        return v.lower()


# ============================================================================
# EXAMPLE 4: Game Character with Stats
# ============================================================================


class GameCharacter(BaseModel):
    """Demonstrates game mechanics with complex constraints."""

    # Character identification
    character_id: PositiveInteger()
    player_id: BigInt(positive=True)
    character_name: Varchar(50)
    character_class: Varchar(20)

    # Level and progression
    level: Integer(min_value=1, max_value=100)
    experience_points: NonNegativeInteger()
    skill_points: NonNegativeInteger()
    prestige_level: TinyInt(min_value=0, max_value=10) = 0

    # Stats that can be negative (debuffs)
    health: Integer(min_value=-100, max_value=9999)
    mana: NonNegativeInteger()
    stamina: Integer(min_value=0, max_value=100)

    # Attribute modifiers (-10 to +10)
    strength_modifier: Integer(min_value=-10, max_value=10) = 0
    defense_modifier: Integer(min_value=-10, max_value=10) = 0
    speed_modifier: SmallInt(min_value=-5, max_value=5) = 0
    intelligence_modifier: TinyInt(min_value=-10, max_value=10) = 0

    # Currency system
    gold: NonNegativeInteger() = 0
    silver: NonNegativeInteger() = 0
    debt: NonPositiveInteger() = 0  # Can owe money (<= 0)
    bank_balance: Integer() = 0  # Can be negative (overdraft)

    # Reputation (-1000 to 1000, in increments of 10)
    reputation: Integer(min_value=-1000, max_value=1000, multiple_of=10) = 0
    honor_points: NonNegativeInteger() = 0
    infamy_points: NonNegativeInteger() = 0

    # Inventory limits
    inventory_slots: TinyInt(min_value=10, max_value=100) = 20
    used_slots: NonNegativeInteger() = 0

    @field_validator("used_slots")
    @classmethod
    def validate_inventory(cls, v: int, info) -> int:
        """Ensure used slots don't exceed total slots."""
        if info.data.get("inventory_slots") and v > info.data["inventory_slots"]:
            raise ValueError("Used slots cannot exceed inventory slots")
        return v

    @property
    def available_slots(self) -> int:
        """Calculate available inventory slots."""
        return self.inventory_slots - self.used_slots

    @property
    def total_money(self) -> int:
        """Total money in base currency (copper)."""
        return (self.gold * 100) + (self.silver * 10)


# ============================================================================
# EXAMPLE 5: API Rate Limiting Configuration
# ============================================================================


class RateLimitConfig(BaseModel):
    """Demonstrates API configuration with precise constraints."""

    config_id: PositiveInteger()
    api_key: Varchar(64)

    # Rate limits (must be multiples for easier calculation)
    requests_per_minute: Integer(min_value=1, max_value=10000, multiple_of=10) = 100
    requests_per_hour: Integer(min_value=1, max_value=100000, multiple_of=100) = 1000
    requests_per_day: Integer(min_value=1, max_value=1000000, multiple_of=1000) = 10000

    # Burst configuration
    burst_size: SmallInt(min_value=1, max_value=1000) = 10
    burst_window_seconds: Integer(min_value=1, max_value=60, multiple_of=5) = 10

    # Cooldown and penalties
    cooldown_seconds: Integer(min_value=0, max_value=3600, multiple_of=30) = 60
    penalty_multiplier: TinyInt(min_value=1, max_value=10) = 2
    max_penalties: TinyInt(min_value=0, max_value=10) = 3

    # Configuration flags
    is_active: Boolean() = True
    allow_burst: Boolean() = True
    strict_mode: Boolean() = False

    # Metadata
    created_at: Timestamp() = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[Timestamp()] = None

    @field_validator("expires_at")
    @classmethod
    def validate_expiry(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Ensure expiry is in the future."""
        if v and info.data.get("created_at") and v <= info.data["created_at"]:
            raise ValueError("Expiry must be after creation time")
        return v


# ============================================================================
# EXAMPLE 6: Scientific Measurement with REAL validation
# ============================================================================


class ScientificMeasurement(BaseModel):
    """Demonstrates floating-point types and REAL validation."""

    measurement_id: BigInt(positive=True)
    experiment_id: Integer(positive=True)
    instrument_id: SmallInt(positive=True)

    # Different float types with SQL implications
    temperature_kelvin: Float()  # General floating point (FLOAT)
    pressure_pascals: Real()  # Single precision (REAL) - validated for range
    energy_joules: Double()  # Double precision (DOUBLE)

    # High precision decimals for exact calculations
    mass_grams: DecimalType(12, 9)  # Up to 999.999999999g
    volume_liters: DecimalType(10, 6)  # Up to 9999.999999L
    concentration_molar: Numeric(8, 6)  # Using Numeric alias

    # Measurement parameters
    measurement_time: Timestamp(precision=6)  # Microsecond precision
    duration_seconds: DecimalType(10, 6)
    uncertainty_percentage: Float() = 0.0

    # Quality indicators
    signal_to_noise_ratio: Float()
    confidence_level: DecimalType(3, 2)  # 0.00 to 9.99

    # Validation flags
    is_calibrated: Boolean() = False
    is_validated: Boolean() = False
    passed_quality_check: Optional[Boolean()] = None

    # Metadata
    operator_id: Optional[Integer()] = None
    notes: Optional[Text(max_length=1000)] = None

    @field_validator("temperature_kelvin")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is above absolute zero."""
        if v < 0:
            raise ValueError("Temperature cannot be below absolute zero")
        if v > 6000:
            raise ValueError("Temperature exceeds reasonable experimental range")
        return v

    @field_validator("confidence_level")
    @classmethod
    def validate_confidence(cls, v: Decimal) -> Decimal:
        """Ensure confidence level is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("Confidence level must be between 0 and 1")
        return v


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================


def demonstrate_basic_usage():
    """Show basic Pydantic usage with python-db-types."""
    print("=" * 80)
    print("BASIC USAGE - Employee Model".center(80))
    print("=" * 80)

    # Create with minimal fields
    emp1 = Employee(
        employee_id=1, email="JOHN.DOE@COMPANY.COM", username="jdoe"  # Will be lowercased
    )
    print(f"\n1. Minimal employee: {emp1.username}")
    print(f"   Email: {emp1.email} (auto-lowercased)")
    print(f"   Department: {emp1.department} (default)")
    print(f"   Hire date: {emp1.hire_date} (auto-set)")

    # Create with type conversions
    emp2 = Employee(
        employee_id=2,
        email="jane.smith@company.com",
        username="jsmith",
        first_name="Jane",
        last_name="Smith",
        # Automatic conversions
        is_active="yes",  # String → Boolean
        is_manager="false",  # String → Boolean
        salary="95000.00",  # String → Decimal
        bonus_percentage="15.50",  # String → Decimal
        hire_date="2020-01-15",  # String → Date
        work_start_time="08:30:00",  # String → Time
    )
    print(f"\n2. Full employee: {emp2.full_name}")
    print(f"   Active: 'yes' → {emp2.is_active}")
    print(f"   Manager: 'false' → {emp2.is_manager}")
    print(f"   Salary: '95000.00' → ${emp2.salary}")
    print(f"   Annual comp: ${emp2.annual_compensation}")

    # JSON serialization
    print("\n3. JSON serialization:")
    json_str = emp2.model_dump_json(indent=2)
    print("   " + "\n   ".join(json_str.split("\n")[:10]))
    print("   ...")


def demonstrate_validation_errors():
    """Show various validation scenarios."""
    print("\n" + "=" * 80)
    print("VALIDATION EXAMPLES".center(80))
    print("=" * 80)

    print("\n1. Missing required field:")
    try:
        Employee(employee_id=1, username="test")  # type: ignore # Missing email
    except ValidationError as e:
        print(f"   ✗ {e.errors()[0]['msg']}")

    print("\n2. Custom validator:")
    try:
        Employee(employee_id=1, email="test@gmail.com", username="test")  # Wrong domain
    except ValidationError as e:
        print(f"   ✗ {e.errors()[0]['msg']}")

    print("\n3. String length:")
    try:
        Employee(
            employee_id=1,
            email="test@company.com",
            username="this_username_is_way_too_long_for_varchar_30",
        )
    except ValidationError as e:
        print(f"   ✗ {e.errors()[0]['msg']}")

    print("\n4. Numeric range:")
    try:
        Employee(
            employee_id=1,
            email="test@company.com",
            username="test",
            years_experience=40000,  # Too big for SMALLINT
        )
    except ValidationError as e:
        print(f"   ✗ {e.errors()[0]['msg']}")

    print("\n5. Decimal precision:")
    try:
        Employee(
            employee_id=1,
            email="test@company.com",
            username="test",
            bonus_percentage="1234.567",  # Too many digits
        )
    except ValidationError as e:
        print(f"   ✗ {e.errors()[0]['msg']}")


def demonstrate_constraints():
    """Show constraint validation with e-commerce example."""
    print("\n" + "=" * 80)
    print("CONSTRAINT VALIDATION - Order System".center(80))
    print("=" * 80)

    # Valid order
    order = OrderItem(
        order_id=123456789,
        product_id=789,
        customer_id=456,
        quantity=3,
        unit_price_cents=2999,  # $29.99
        discount_amount_cents=500,  # $5.00
        discount_percentage=15,  # Valid: multiple of 5
        tax_rate_basis_points=875,  # 8.75%
        status="confirmed",
    )

    print(f"\nOrder {order.order_id}:")
    print(f"  Product: {order.product_id} x {order.quantity}")
    print(f"  Unit price: ${order.unit_price_cents/100:.2f}")
    print(f"  Subtotal: ${order.subtotal_cents/100:.2f}")
    print(f"  Discount: ${order.discount_amount_cents/100:.2f} ({order.discount_percentage}%)")
    print(f"  Tax: {order.tax_rate_basis_points/100:.2f}%")
    print(f"  Total: ${order.total_cents/100:.2f}")

    # Constraint violations
    print("\nConstraint violations:")

    try:
        OrderItem(
            order_id=0,  # Must be positive
            product_id=1,
            customer_id=1,
            quantity=1,
            unit_price_cents=100,
            discount_amount_cents=0,
            discount_percentage=0,
            tax_rate_basis_points=0,
        )
    except ValidationError as e:
        print(f"  ✗ Order ID: {e.errors()[0]['msg']}")

    try:
        OrderItem(
            order_id=1,
            product_id=1,
            customer_id=1,
            quantity=0,  # Must be >= 1
            unit_price_cents=100,
            discount_amount_cents=0,
            discount_percentage=0,
            tax_rate_basis_points=0,
        )
    except ValidationError as e:
        print(f"  ✗ Quantity: {e.errors()[0]['msg']}")


def demonstrate_user_account():
    """Show user account with preferences."""
    print("\n" + "=" * 80)
    print("USER ACCOUNT - With Preferences".center(80))
    print("=" * 80)

    user = UserAccount(
        user_id=12345,
        username="JaneDoe_123",  # Will be lowercased
        email="jane.doe@example.com",
        age=28,
        years_active=3,
        credit_score=750,
        credit_balance_cents=50000,  # $500.00
        loyalty_points=1500,
        cashback_percentage=Decimal("2.5"),
        notification_hour=9,  # 9 AM
        timezone_offset=-5,  # EST
        is_verified=True,
        is_premium=True,
        account_type="premium",
    )

    print(f"\nUser Account: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Age: {user.age}, Active for: {user.years_active} years")
    print(f"  Credit Score: {user.credit_score}")
    print(f"  Balance: ${user.credit_balance_cents/100:.2f}")
    print(f"  Loyalty: {user.loyalty_points} points")
    print(f"  Cashback: {user.cashback_percentage}%")
    print(f"  Notifications: {user.notification_hour}:00 (GMT{user.timezone_offset:+d})")
    print(
        f"  Status: {'✓' if user.is_verified else '✗'} Verified, "
        + f"{'✓' if user.is_premium else '✗'} Premium"
    )


def demonstrate_game_character():
    """Show game character with complex stats."""
    print("\n" + "=" * 80)
    print("GAME CHARACTER - Complex Constraints".center(80))
    print("=" * 80)

    character = GameCharacter(
        character_id=42,
        player_id=1001,
        character_name="Aragorn",
        character_class="Ranger",
        level=45,
        experience_points=125000,
        skill_points=23,
        prestige_level=2,
        health=750,
        mana=200,
        stamina=85,
        strength_modifier=5,
        defense_modifier=3,
        speed_modifier=2,
        intelligence_modifier=-1,
        gold=1250,
        silver=85,
        debt=-200,  # Owes 200
        bank_balance=5000,
        reputation=400,  # Multiple of 10
        honor_points=350,
        infamy_points=50,
        inventory_slots=40,
        used_slots=25,
    )

    print(f"\n{character.character_name} - Level {character.level} {character.character_class}")
    print(f"  Prestige: {'★' * character.prestige_level}")
    print(f"  HP: {character.health} | MP: {character.mana} | Stamina: {character.stamina}")
    print(
        f"  Modifiers: STR {character.strength_modifier:+d}, "
        + f"DEF {character.defense_modifier:+d}, "
        + f"SPD {character.speed_modifier:+d}, INT {character.intelligence_modifier:+d}"
    )
    print(f"  Money: {character.gold}g {character.silver}s (Total: {character.total_money} copper)")
    print(f"  Debt: {character.debt} | Bank: {character.bank_balance}")
    print(
        f"  Reputation: {character.reputation} "
        + f"(Honor: {character.honor_points}, Infamy: {character.infamy_points})"
    )
    print(
        f"  Inventory: {character.used_slots}/{character.inventory_slots} slots "
        + f"({character.available_slots} free)"
    )


def demonstrate_tinyint_usage():
    """Show TINYINT with rate limiting config."""
    print("\n" + "=" * 80)
    print("TINYINT USAGE - Rate Limiting".center(80))
    print("=" * 80)

    config = RateLimitConfig(
        config_id=1,
        api_key="sk_live_abcdef123456",
        requests_per_minute=100,  # Multiple of 10
        requests_per_hour=3000,  # Multiple of 100
        requests_per_day=50000,  # Multiple of 1000
        burst_size=20,
        burst_window_seconds=10,
        cooldown_seconds=120,  # Multiple of 30
        penalty_multiplier=3,
        max_penalties=5,
    )

    print(f"\nRate Limit Config #{config.config_id}:")
    print(f"  API Key: {config.api_key[:10]}...")
    print(
        f"  Limits: {config.requests_per_minute}/min, "
        + f"{config.requests_per_hour}/hr, {config.requests_per_day}/day"
    )
    print(f"  Burst: {config.burst_size} requests in {config.burst_window_seconds}s")
    print(
        f"  Penalties: {config.penalty_multiplier}x multiplier, "
        + f"max {config.max_penalties} strikes"
    )
    print(f"  Cooldown: {config.cooldown_seconds}s")
    print(
        f"  Flags: Active={config.is_active}, Burst={config.allow_burst}, "
        + f"Strict={config.strict_mode}"
    )


def demonstrate_scientific_measurement():
    """Show scientific measurement with REAL validation."""
    print("\n" + "=" * 80)
    print("SCIENTIFIC MEASUREMENT - Float Types".center(80))
    print("=" * 80)

    # Valid measurement
    measurement = ScientificMeasurement(
        measurement_id=1001,
        experiment_id=42,
        instrument_id=5,
        temperature_kelvin=298.15,  # 25°C
        pressure_pascals=101325.0,  # 1 atm
        energy_joules=1234.5678,
        mass_grams=Decimal("15.123456789"),
        volume_liters=Decimal("2.500000"),
        concentration_molar=Decimal("0.100000"),
        measurement_time=datetime.now(timezone.utc),
        duration_seconds=Decimal("3600.000000"),
        uncertainty_percentage=0.05,
        signal_to_noise_ratio=42.5,
        confidence_level=Decimal("0.95"),
        is_calibrated=True,
        is_validated=True,
        passed_quality_check=True,
    )

    print(f"\nMeasurement #{measurement.measurement_id}:")
    print(
        f"  Temperature: {measurement.temperature_kelvin}K "
        + f"({measurement.temperature_kelvin - 273.15:.1f}°C)"
    )
    print(f"  Pressure: {measurement.pressure_pascals} Pa (REAL type)")
    print(f"  Energy: {measurement.energy_joules} J (DOUBLE type)")
    print(f"  Mass: {measurement.mass_grams}g (precise decimal)")
    print(f"  Volume: {measurement.volume_liters}L")
    print(f"  Concentration: {measurement.concentration_molar}M (using Numeric alias)")
    print(
        f"  Quality: SNR={measurement.signal_to_noise_ratio}, "
        + f"Confidence={measurement.confidence_level}"
    )
    print(
        f"  Status: {'✓' if measurement.is_calibrated else '✗'} Calibrated, "
        + f"{'✓' if measurement.is_validated else '✗'} Validated, "
        + f"{'✓' if measurement.passed_quality_check else '✗'} QC Passed"
    )

    # Show REAL validation
    print("\n  Testing REAL type validation:")
    try:
        # This will fail because it exceeds single precision range
        ScientificMeasurement(
            measurement_id=2,
            experiment_id=1,
            instrument_id=1,
            temperature_kelvin=300,
            pressure_pascals=1e39,  # Too large for REAL
            energy_joules=100,
            mass_grams=Decimal("1"),
            volume_liters=Decimal("1"),
            concentration_molar=Decimal("1"),
            measurement_time=datetime.now(timezone.utc),
            duration_seconds=Decimal("1"),
            signal_to_noise_ratio=1,
            confidence_level=Decimal("0.5"),
        )
    except ValidationError as e:
        print(f"    ✗ REAL validation: {e.errors()[0]['msg']}")


def demonstrate_field_updates():
    """Show validation on field assignment."""
    print("\n" + "=" * 80)
    print("FIELD UPDATE VALIDATION".center(80))
    print("=" * 80)

    emp = Employee(
        employee_id=100,
        email="update@company.com",
        username="update_test",
        salary=Decimal("80000"),
        bonus_percentage=Decimal("10"),
    )

    print("\nOriginal values:")
    print(f"  Email: {emp.email}")
    print(f"  Salary: ${emp.salary}")
    print(f"  Annual comp: ${emp.annual_compensation}")

    # Valid updates
    emp.salary = Decimal("90000")
    emp.bonus_percentage = Decimal("15")
    print("\nAfter valid updates:")
    print(f"  Salary: ${emp.salary}")
    print(f"  Annual comp: ${emp.annual_compensation}")

    # Invalid updates (caught by validate_assignment=True)
    print("\nInvalid updates:")
    try:
        emp.email = "wrong@gmail.com"  # Wrong domain
    except ValidationError as e:
        print(f"  ✗ Email: {e.errors()[0]['msg']}")

    try:
        emp.salary = Decimal("-1000")  # Negative
    except ValidationError as e:
        print(f"  ✗ Salary: {e.errors()[0]['msg']}")


def demonstrate_boolean_conversions():
    """Show flexible boolean parsing."""
    print("\n" + "=" * 80)
    print("BOOLEAN TYPE CONVERSIONS".center(80))
    print("=" * 80)

    print("\nBoolean accepts various formats:")
    test_values = ["yes", "no", "1", "0", "true", "false", "Y", "N", "on", "off"]

    for val in test_values:
        emp = Employee(
            employee_id=999, email="bool@company.com", username="bool_test", is_active=val
        )
        print(f"  '{val}' → {emp.is_active}")


def main():
    """Run all demonstrations."""
    demonstrate_basic_usage()
    demonstrate_validation_errors()
    demonstrate_constraints()
    demonstrate_user_account()
    demonstrate_game_character()
    demonstrate_tinyint_usage()
    demonstrate_scientific_measurement()
    demonstrate_field_updates()
    demonstrate_boolean_conversions()

    print("\n" + "=" * 80)
    print("KEY FEATURES WITH PYDANTIC".center(80))
    print("=" * 80)
    print(
        """
✓ Same clean syntax as dataclasses: Varchar(50), Integer(), etc.
✓ Automatic validation on creation AND assignment
✓ Type conversion: strings → dates, decimals, booleans
✓ Custom field validators with @field_validator
✓ JSON serialization with proper encoding
✓ Computed properties and methods
✓ All constraint types: PositiveInteger(), min_value, max_value, multiple_of
✓ TINYINT for small values (8-bit)
✓ REAL vs FLOAT with proper validation
✓ Numeric alias for SQL standard naming
✓ Rich error messages with field paths
"""
    )


if __name__ == "__main__":
    main()
