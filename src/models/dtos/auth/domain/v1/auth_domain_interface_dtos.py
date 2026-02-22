from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterUserRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    first_name: str = Field(..., min_length=3, max_length=50)
    last_name: str = Field(..., min_length=3, max_length=50)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)


class RegisterUserInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    first_name: str
    last_name: str
    username: str
    password: str


class RegisterUserOutputDTOV1(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uuid: UUID
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
