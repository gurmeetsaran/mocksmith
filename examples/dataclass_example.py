"""Comprehensive dataclass example demonstrating python-db-types features."""

from dataclasses import dataclass
from typing import Optional, Annotated
from datetime import date, datetime, time
from decimal import Decimal

from db_types import (
    Varchar, Char, Text,
    Integer, BigInt, SmallInt, DecimalType, Money,
    Date, Time, Timestamp,
    Boolean,
    Binary, Blob
)
# For db_field, we need the actual type classes
from db_types.types.string import TEXT
from db_types.types.numeric import INTEGER
from db_types.dataclass_integration import validate_dataclass, db_field


@validate_dataclass
@dataclass
class Employee:
    """Demonstrates all key features of python-db-types with dataclasses.
    
    Note: Dataclasses can now use the same clean syntax as Pydantic!
    """
    
    # === REQUIRED FIELDS ===
    # These fields must be provided when creating an instance
    
    employee_id: Integer()
    email: Varchar(255)
    username: Varchar(30)
    
    # === OPTIONAL FIELDS ===
    # Use Optional[Type] for optional fields
    
    first_name: Optional[Varchar(50)] = None
    last_name: Optional[Varchar(50)] = None
    middle_name: Optional[Varchar(50)] = None
    bio: Optional[Text(max_length=1000)] = None
    phone: Optional[Varchar(20)] = None
    
    # === FIELDS WITH DEFAULTS ===
    # These have default values, so they're optional when creating instances
    
    department: Varchar(50) = "Engineering"
    employee_code: Char(10) = "EMP0000000"
    is_active: Boolean() = True
    is_manager: Boolean() = False
    
    # === NUMERIC FIELDS WITH VALIDATION ===
    
    salary: Money() = Decimal("0.00")
    bonus_percentage: DecimalType(5, 2) = Decimal("0.00")
    years_experience: SmallInt() = 0
    vacation_days: Integer() = 20
    
    # === DATE/TIME FIELDS ===
    
    hire_date: Date() = date.today()
    birth_date: Optional[Date()] = None
    last_login: Optional[Timestamp()] = None
    work_start_time: Optional[Time(precision=0)] = None
    
    # === BINARY DATA ===
    
    avatar: Optional[Blob(max_length=1048576)] = None
    
    # === ALTERNATIVE: Using db_field (still works) ===
    # This is another way to define fields with database types
    
    notes: str = db_field(TEXT(), default="")
    employee_rank: int = db_field(INTEGER(), default=1)


def demonstrate_dataclass_features():
    """Show all key features and validations."""
    
    print("=" * 70)
    print("PYTHON-DB-TYPES WITH DATACLASSES".center(70))
    print("=" * 70)
    
    # 1. Creating a valid employee with required fields only
    print("\n1. Creating employee with required fields only:")
    employee1 = Employee(
        employee_id=1,
        email="john.doe@company.com",
        username="jdoe"
    )
    print(f"   Created: {employee1.username} ({employee1.email})")
    print(f"   Department: {employee1.department} (default)")
    print(f"   Active: {employee1.is_active} (default)")
    print(f"   Salary: ${employee1.salary} (default)")
    
    # 2. Creating employee with all fields
    print("\n2. Creating employee with optional fields:")
    employee2 = Employee(
        employee_id=2,
        email="jane.smith@company.com",
        username="jsmith",
        first_name="Jane",
        last_name="Smith",
        bio="Senior Python developer with 10 years experience",
        phone="+1-555-0123",
        salary=Decimal("95000.00"),
        bonus_percentage=Decimal("15.50"),
        years_experience=10,
        hire_date=date(2014, 3, 15),
        birth_date=date(1990, 5, 20),
        is_manager=True
    )
    print(f"   Created: {employee2.first_name} {employee2.last_name}")
    print(f"   Salary: ${employee2.salary}")
    print(f"   Bonus: {employee2.bonus_percentage}%")
    print(f"   Manager: {employee2.is_manager}")
    
    # 3. Type conversions
    print("\n3. Automatic type conversions:")
    employee3 = Employee(
        employee_id=3,
        email="bob@company.com",
        username="bob",
        is_active="yes",           # String -> Boolean
        is_manager="false",         # String -> Boolean
        salary="75000.00",          # String -> Decimal
        hire_date="2020-01-15",     # String -> Date
    )
    print(f"   is_active: 'yes' → {employee3.is_active} (bool)")
    print(f"   is_manager: 'false' → {employee3.is_manager} (bool)")
    print(f"   salary: '75000.00' → ${employee3.salary} (Decimal)")
    print(f"   hire_date: '2020-01-15' → {employee3.hire_date} (date)")
    
    # 4. Validation errors
    print("\n4. Validation examples:")
    
    # 4a. String too long
    print("   Testing VARCHAR length validation...")
    try:
        Employee(
            employee_id=4,
            email="test@company.com",
            username="this_username_is_way_too_long_for_the_field"  # > 30 chars
        )
    except ValueError as e:
        print(f"   ✗ Username validation: {e}")
    
    # 4b. Number out of range
    print("   Testing SMALLINT range validation...")
    try:
        Employee(
            employee_id=5,
            email="test2@company.com",
            username="test2",
            years_experience=40000  # Too big for SMALLINT (-32768 to 32767)
        )
    except ValueError as e:
        print(f"   ✗ Years validation: {e}")
    
    # 4c. Decimal precision
    print("   Testing DECIMAL precision validation...")
    try:
        Employee(
            employee_id=6,
            email="test3@company.com",
            username="test3",
            bonus_percentage=Decimal("1000.00")  # Too big for DECIMAL(5,2)
        )
    except ValueError as e:
        print(f"   ✗ Bonus validation: {e}")
    
    # 4d. NULL in required field
    print("   Testing required field constraint...")
    try:
        Employee(
            employee_id=None,  # Required field
            email="test4@company.com",
            username="test4"
        )
    except ValueError as e:
        print(f"   ✗ NULL validation: {e}")
    
    # 5. SQL serialization
    print("\n5. Converting to SQL-compatible format:")
    sql_data = employee2.to_sql_dict()
    print("   SQL data (selected fields):")
    for key in ['employee_id', 'email', 'salary', 'hire_date', 'is_manager']:
        if key in sql_data:
            print(f"     {key}: {sql_data[key]!r}")
    
    # 6. Show database types
    print("\n6. Database type information:")
    db_types = employee2.get_db_types()
    print(f"   Total DB fields: {len(db_types)}")
    for field_name, db_type in list(db_types.items())[:5]:
        print(f"   {field_name}: {db_type}")
    
    # 7. CHAR vs VARCHAR behavior
    print("\n7. CHAR vs VARCHAR behavior:")
    employee4 = Employee(
        employee_id=7,
        email="char@test.com",
        username="chartest",
        employee_code="EMP123"  # Will be padded to 10 chars
    )
    sql_dict = employee4.to_sql_dict()
    print(f"   Input code: 'EMP123' (length {len('EMP123')})")
    print(f"   Stored as: '{sql_dict['employee_code']}' (length {len(sql_dict['employee_code'])})")
    
    # 8. Boolean conversions
    print("\n8. Boolean type accepts various formats:")
    bool_values = ["yes", "no", "1", "0", "true", "false"]
    for val in bool_values:
        emp = Employee(
            employee_id=99,
            email="bool@company.com",
            username="bool",
            is_active=val
        )
        print(f"   '{val}' → {emp.is_active}")
    
    # 9. Working with NULL values
    print("\n9. NULL handling for optional fields:")
    minimal = Employee(
        employee_id=100,
        email="minimal@company.com",
        username="minimal"
    )
    print(f"   first_name: {minimal.first_name} (None = NULL)")
    print(f"   bio: {minimal.bio} (None = NULL)")
    print(f"   birth_date: {minimal.birth_date} (None = NULL)")
    
    print("\n" + "=" * 70)
    print("Key Points:")
    print("- Dataclasses now support clean syntax: Varchar(50) instead of Annotated[str, VARCHAR(50)]")
    print("- Optional fields: Optional[Type] = None (same as Pydantic!)")
    print("- All validations happen at Python level before DB insertion")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_dataclass_features()