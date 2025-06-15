"""Comprehensive Pydantic example demonstrating python-db-types features."""

from typing import Optional
from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError, field_validator
from db_types import (
    Varchar, Char, Text,
    Integer, BigInt, SmallInt, Money, DecimalType,
    Date, Time, Timestamp, DateTime,
    Boolean,
    Binary, Blob
)


class Employee(BaseModel):
    """Demonstrates all key features of python-db-types with Pydantic.
    
    This single model shows:
    - Required vs optional fields
    - Type conversions
    - Validation
    - Default values
    - Custom validators
    - JSON serialization
    """
    
    # === REQUIRED FIELDS ===
    # No default value = required when creating instance
    
    employee_id: Integer()
    email: Varchar(255) 
    username: Varchar(30)
    
    # === OPTIONAL FIELDS ===
    # Use Optional[Type] = None for optional fields
    
    first_name: Optional[Varchar(50)] = None
    last_name: Optional[Varchar(50)] = None
    middle_name: Optional[Varchar(50)] = None
    bio: Optional[Text(max_length=1000)] = None    # Text with max length
    phone: Optional[Varchar(20)] = None
    
    # === FIELDS WITH DEFAULTS ===
    # Default values make fields optional
    
    department: Varchar(50) = "Engineering"
    employee_code: Char(10) = "EMP0000000"         # Fixed-length, padded
    is_active: Boolean() = True
    is_manager: Boolean() = False
    
    # === NUMERIC FIELDS ===
    
    salary: Money() = Decimal("0.00")               # DECIMAL(19,4) for money
    bonus_percentage: DecimalType(5, 2) = Decimal("0.00")  # Max 999.99%
    years_experience: SmallInt() = 0               # -32768 to 32767
    vacation_days: Integer() = 20                  # Standard integer
    
    # === DATE/TIME FIELDS ===
    
    hire_date: Date() = Field(default_factory=date.today)
    birth_date: Optional[Date()] = None
    last_login: Optional[Timestamp()] = None       # With timezone
    last_review: Optional[DateTime()] = None       # Without timezone
    work_start_time: Time(precision=0) = "09:00:00"  # No fractional seconds
    
    # === BINARY DATA ===
    
    avatar: Optional[Blob(max_length=1048576)] = None  # 1MB max
    employee_badge: Optional[Binary(16)] = None    # Fixed 16 bytes
    
    # === COMPUTED FIELDS ===
    
    @property
    def full_name(self) -> str:
        """Computed property combining names."""
        parts = [n for n in [self.first_name, self.middle_name, self.last_name] if n]
        return " ".join(parts) if parts else self.username
    
    @property
    def annual_compensation(self) -> Decimal:
        """Total compensation including bonus."""
        bonus = self.salary * (self.bonus_percentage / 100)
        return self.salary + bonus
    
    # === CUSTOM VALIDATORS ===
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Additional email validation."""
        if '@' not in v:
            raise ValueError('Invalid email format')
        if not v.lower().endswith('@company.com'):
            raise ValueError('Email must be @company.com domain')
        return v.lower()
    
    @field_validator('salary')
    @classmethod
    def validate_salary(cls, v: Decimal) -> Decimal:
        """Ensure salary is positive."""
        if v < 0:
            raise ValueError('Salary cannot be negative')
        return v
    
    # === PYDANTIC CONFIGURATION ===
    
    class Config:
        # Enable validation on assignment
        validate_assignment = True
        # Custom JSON encoding
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
            bytes: lambda v: v.hex() if v else None,
        }


def demonstrate_pydantic_features():
    """Show all key features and validations."""
    
    print("=" * 70)
    print("PYTHON-DB-TYPES WITH PYDANTIC".center(70))
    print("=" * 70)
    
    # 1. Creating with required fields only
    print("\n1. Creating employee with required fields only:")
    employee1 = Employee(
        employee_id=1,
        email="john.doe@company.com",
        username="jdoe"
    )
    print(f"   Created: {employee1.username}")
    print(f"   Email: {employee1.email}")
    print(f"   Department: {employee1.department} (default)")
    print(f"   Active: {employee1.is_active} (default)")
    
    # 2. Creating with type conversions
    print("\n2. Automatic type conversions:")
    employee2 = Employee(
        employee_id=2,
        email="JANE.SMITH@COMPANY.COM",  # Will be lowercased
        username="jsmith",
        first_name="Jane",
        last_name="Smith",
        # Type conversions
        is_active="yes",              # String → Boolean (True)
        is_manager="false",           # String → Boolean (False)
        salary="95000.00",            # String → Decimal
        bonus_percentage="15.5",      # String → Decimal
        hire_date="2020-01-15",       # String → Date
        work_start_time="08:30:00",   # String → Time
    )
    print(f"   Name: {employee2.full_name}")
    print(f"   Email converted: 'JANE.SMITH@COMPANY.COM' → '{employee2.email}'")
    print(f"   Active: 'yes' → {employee2.is_active}")
    print(f"   Manager: 'false' → {employee2.is_manager}")
    print(f"   Salary: '95000.00' → ${employee2.salary}")
    print(f"   Annual comp: ${employee2.annual_compensation}")
    
    # 3. Validation errors
    print("\n3. Validation examples:")
    
    # 3a. Missing required field
    try:
        Employee(employee_id=3, username="test")  # Missing email
    except ValidationError as e:
        print(f"   ✗ Missing required field: {e.errors()[0]['msg']}")
    
    # 3b. String too long
    try:
        Employee(
            employee_id=4,
            email="test@company.com",
            username="this_username_is_way_too_long_for_varchar_30"
        )
    except ValidationError as e:
        print(f"   ✗ Username too long: {e.errors()[0]['msg']}")
    
    # 3c. Custom validator
    try:
        Employee(
            employee_id=5,
            email="test@gmail.com",  # Wrong domain
            username="test"
        )
    except ValidationError as e:
        print(f"   ✗ Email validation: {e.errors()[0]['msg']}")
    
    # 3d. Number out of range
    try:
        Employee(
            employee_id=6,
            email="test@company.com",
            username="test",
            years_experience=40000  # Too big for SMALLINT
        )
    except ValidationError as e:
        print(f"   ✗ Years too big: {e.errors()[0]['msg']}")
    
    # 3e. Decimal precision
    try:
        Employee(
            employee_id=7,
            email="test2@company.com",
            username="test2",
            bonus_percentage="1234.567"  # Too many digits for DECIMAL(5,2)
        )
    except ValidationError as e:
        print(f"   ✗ Decimal precision: {e.errors()[0]['msg']}")
    
    # 3f. Boolean conversion
    print("\n   Boolean conversion examples:")
    for value in ["yes", "no", "1", "0", "true", "false", "Y", "N"]:
        emp = Employee(
            employee_id=99,
            email="bool@company.com",
            username="bool",
            is_active=value
        )
        print(f"     '{value}' → {emp.is_active}")
    
    # 4. Working with optional fields
    print("\n4. Optional fields:")
    employee3 = Employee(
        employee_id=10,
        email="minimal@company.com",
        username="minimal",
        # All optional fields will be None
    )
    print(f"   first_name: {employee3.first_name}")
    print(f"   bio: {employee3.bio}")
    print(f"   birth_date: {employee3.birth_date}")
    
    # 5. JSON serialization
    print("\n5. JSON serialization:")
    employee4 = Employee(
        employee_id=11,
        email="json@company.com",
        username="json_test",
        salary=Decimal("85000.00"),
        hire_date=date(2021, 6, 15),
        last_login=datetime.now(timezone.utc)
    )
    json_data = employee4.model_dump_json(indent=2)
    print("   JSON output (truncated):")
    for line in json_data.split('\n')[:8]:
        print(f"   {line}")
    print("   ...")
    
    # 6. CHAR field behavior
    print("\n6. CHAR field padding:")
    employee5 = Employee(
        employee_id=12,
        email="char@company.com",
        username="chartest",
        employee_code="EMP123"  # Will be padded
    )
    # Note: In Pydantic, CHAR padding happens during serialization
    print(f"   Input: 'EMP123' (length {len('EMP123')})")
    print(f"   Stored in model: '{employee5.employee_code}' (length {len(employee5.employee_code)})")
    
    # 7. Validation on assignment
    print("\n7. Validation on assignment:")
    try:
        employee5.email = "invalid@gmail.com"  # Wrong domain
    except ValidationError as e:
        print(f"   ✗ Assignment validation: {e.errors()[0]['msg']}")
    
    # 8. Direct assignment with validation
    print("\n8. Direct field updates with validation:")
    employee6 = Employee(
        employee_id=20,
        email="update@company.com",
        username="update_test",
        salary="80000.00",
        bonus_percentage="10.0"
    )
    print(f"   Original salary: ${employee6.salary}")
    print(f"   Original annual comp: ${employee6.annual_compensation}")
    
    # Update fields (validation runs automatically due to validate_assignment=True)
    employee6.salary = Decimal("92000.00")
    employee6.bonus_percentage = Decimal("18.5")
    employee6.is_manager = True
    
    print(f"   Updated salary: ${employee6.salary}")
    print(f"   Updated bonus: {employee6.bonus_percentage}%")
    print(f"   New annual comp: ${employee6.annual_compensation}")
    
    print("\n" + "=" * 70)
    print("Pydantic provides automatic validation, type conversion, and serialization!")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_pydantic_features()