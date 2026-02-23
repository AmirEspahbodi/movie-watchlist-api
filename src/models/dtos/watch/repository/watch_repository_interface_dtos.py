from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from pydantic import BaseModel, ConfigDict


class CreateWatchCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_uuid: UUID
    movie_uuid: UUID


class CreateWatchResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    watch_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    created_at: datetime
    updated_at: datetime


class CheckWatchExistsQueryDTO(BaseDTO):
    user_uuid: UUID
    movie_uuid: UUID
