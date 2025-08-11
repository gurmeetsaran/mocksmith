import dataclasses
from typing import Annotated, Literal

import pydantic
from pydantic import BaseModel

from mocksmith import (
    Date,
    Integer,
    PositiveInteger,
    TinyInt,
    Varchar,
    mockable,
)


# ❌ PROBLEM: Dataclasses don't validate - this accepts invalid values!
# Note: @validate_dataclass doesn't work with the new type system
@mockable
@dataclasses.dataclass
class UserDataclass:
    id: Integer()
    username: Varchar(50)
    hello: Annotated[int, TinyInt(gt=5)]  # Correct annotation but NO validation in dataclass
    # hello2: TINYINT  # ❌ WRONG - this is just a type hint, remove it


# This accepts 4000 without validation (dataclass limitation):
user_dc = UserDataclass.mock(hello=4000)  # Accepts invalid value!
print(f"❌ Dataclass accepted invalid value: hello={user_dc.hello}")


# ✅ SOLUTION: Use Pydantic BaseModel for validation
@mockable
class User(BaseModel):  # Use BaseModel for automatic validation
    id: PositiveInteger()  # Better: use specialized type
    username: Varchar(50)
    website: pydantic.HttpUrl
    email: pydantic.EmailStr
    birth_date: Date()
    favourite_color: Literal["green", "yellow", "red"]
    hello: Annotated[
        int, TinyInt(gt=5, le=120)
    ]  # Validates: 5 < value <= 120 (max 127 for TINYINT)


# This now validates properly:
user1 = User.mock(hello=6)  # Must be > 5, not >= 5
print(f"✅ Valid user: {user1.username}, hello={user1.hello}")

# This would raise ValidationError:
# user2 = User.mock(hello=4000)  # ❌ Raises ValidationError: exceeds TINYINT max of 127
