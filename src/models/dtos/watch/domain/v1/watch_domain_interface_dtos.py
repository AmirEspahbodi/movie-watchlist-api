from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from pydantic import BaseModel, ConfigDict


class WatchMovieRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID


class WatchMovieInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID
    user_uuid: UUID


class WatchMovieOutputDTOV1(BaseDTO):
    watch_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    created_at: datetime
    updated_at: datetime
