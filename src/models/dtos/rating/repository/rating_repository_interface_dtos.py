from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict

from src.models.types.rating_sort_type import RatingSortColumnType


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


class RatedMovieItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rate_uuid: UUID
    movie_uuid: UUID
    title: str
    description: str | None
    genre_uuid: UUID
    score: int
    rated_at: datetime


class GetMyRatingsQueryDTO(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[RatingSortColumnType]


class GetMyRatingsResponseDTO(BaseDTO):
    ratings: list[RatedMovieItemDTO]
    total: int


class GetUserRatingsQueryDTO(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[RatingSortColumnType]


class GetUserRatingsResponseDTO(BaseDTO):
    ratings: list[RatedMovieItemDTO]
    total: int


class RaterUserItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rate_uuid: UUID
    user_uuid: UUID
    first_name: str
    last_name: str
    email: str
    score: int
    rated_at: datetime


class GetMovieRatersQueryDTO(BaseDTO):
    movie_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[RatingSortColumnType]


class GetMovieRatersResponseDTO(BaseDTO):
    raters: list[RaterUserItemDTO]
    total: int
