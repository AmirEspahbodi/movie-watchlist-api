from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict

from src.models.types.movie_sort_type import MovieSortColumnType


class CreateMovieCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str | None = None
    genre_uuid: UUID


class CreateMovieResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    movie_uuid: UUID
    title: str
    description: str | None
    genre_uuid: UUID
    created_at: datetime
    updated_at: datetime


class BulkCreateMovieCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movies: list[CreateMovieCommandDTO]


class BulkCreateMovieResponseDTO(BaseModel):
    movies: list[CreateMovieResponseDTO]


class GetMovieQueryDTO(BaseDTO):
    movie_uuid: UUID


class GetMovieResponseDTO(BaseDTO):
    movie_uuid: UUID
    title: str
    description: str | None = None
    genre_uuid: UUID
    created_at: datetime
    updated_at: datetime


class MovieItemDTO(BaseDTO):
    movie_uuid: UUID
    title: str
    description: str | None = None
    genre_uuid: UUID
    created_at: datetime


class SearchMovieQueryDTO(BaseDTO):
    title: str | None = None
    genre_uuid: UUID | None = None
    pagination: PaginationDTO
    sort_info: SortDTO[MovieSortColumnType]


class SearchMovieResponseDTO(BaseDTO):
    movies: list[MovieItemDTO]
    total: int


class UpdateMovieCommandDTO(BaseDTO):
    movie_uuid: UUID
    title: str | None = None
    description: str | None = None
    genre_uuid: UUID | None = None


class DeleteMovieCommandDTO(BaseDTO):
    movie_uuid: UUID
