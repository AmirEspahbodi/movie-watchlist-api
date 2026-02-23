from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from pydantic import BaseModel, ConfigDict, Field


class RateMovieRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID
    score: int = Field(..., ge=1, le=10)


class RateMovieInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID
    user_uuid: UUID
    score: int


class RateMovieOutputDTOV1(BaseDTO):
    rate_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    score: int
    created_at: datetime
    updated_at: datetime


class UpdateRatingRestInputDTOV1(BaseDTO):
    score: int = Field(..., ge=1, le=10)


class UpdateRatingInputDTOV1(BaseDTO):
    rate_uuid: UUID
    user_uuid: UUID
    score: int
