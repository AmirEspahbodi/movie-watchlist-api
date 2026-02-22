from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.range_dtos import DateRangeDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict, EmailStr, StrictStr

from src.models.types.user_sort_type import UserSortColumnType


class CreateUserCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    first_name: str
    last_name: str
    username: str
    hashed_password: str
    is_active: bool = True
    is_super_user: bool = False


class CreateUserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uuid: UUID
    email: EmailStr
    username: str
    is_active: bool
    is_super_user: bool
    created_at: datetime
    updated_at: datetime


class GetUserQueryDTO(BaseDTO):
    user_uuid: UUID


class GetUserResponseDTO(BaseDTO):
    user_uuid: UUID
    first_name: StrictStr
    last_name: StrictStr
    birth_date: datetime | None = None
    is_super_user: bool
    created_at: datetime


class UserItemDTO(BaseDTO):
    user_uuid: UUID
    first_name: StrictStr
    last_name: StrictStr
    birth_date: datetime | None = None
    is_super_user: bool
    created_at: datetime


class SearchUserQueryDTO(BaseDTO):
    first_name: StrictStr | None = None
    last_name: StrictStr | None = None
    birth_date_range: DateRangeDTO | None = None
    pagination: PaginationDTO
    sort_info: SortDTO[UserSortColumnType]


class SearchUserResponseDTO(BaseDTO):
    users: list[UserItemDTO]
    total: int


class UpdateUserCommandDTO(BaseDTO):
    user_uuid: UUID
    first_name: StrictStr | None = None
    last_name: StrictStr | None = None
    birth_date: datetime | None = None
    is_super_user: bool | None = None


class DeleteUserCommandDTO(BaseDTO):
    user_uuid: UUID


class GetUserByEmailQueryDTO(BaseDTO):
    email: EmailStr


class GetUserByEmailResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uuid: UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    hashed_password: str
    is_active: bool
    is_super_user: bool
    created_at: datetime
    updated_at: datetime


class GetUserFullByUUIDQueryDTO(BaseDTO):
    user_uuid: UUID


class GetUserFullByUUIDResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uuid: UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_super_user: bool
    created_at: datetime
