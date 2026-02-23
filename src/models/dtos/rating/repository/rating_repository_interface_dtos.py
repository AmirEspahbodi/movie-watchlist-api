from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from pydantic import BaseModel, ConfigDict


class CreateRatingCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_uuid: UUID
    movie_uuid: UUID
    score: int


class CreateRatingResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rate_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    score: int
    created_at: datetime
    updated_at: datetime


class CheckRatingExistsQueryDTO(BaseDTO):
    user_uuid: UUID
    movie_uuid: UUID


class GetRatingQueryDTO(BaseDTO):
    rate_uuid: UUID
    user_uuid: UUID


class GetRatingResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rate_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    score: int


class UpdateRatingCommandDTO(BaseDTO):
    rate_uuid: UUID
    user_uuid: UUID
    score: int
