from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict

from src.models.types.genre_sort_type import GenreSortColumnType


class CreateGenreCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None


class CreateGenreResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    genre_uuid: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class BulkCreateGenreCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    genres: list[CreateGenreCommandDTO]


class BulkCreateGenreResponseDTO(BaseModel):
    genres: list[CreateGenreResponseDTO]


class GetGenreQueryDTO(BaseDTO):
    genre_uuid: UUID


class GetGenreResponseDTO(BaseDTO):
    genre_uuid: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class GenreItemDTO(BaseDTO):
    genre_uuid: UUID
    name: str
    description: str | None = None
    created_at: datetime


class SearchGenreQueryDTO(BaseDTO):
    name: str | None = None
    pagination: PaginationDTO
    sort_info: SortDTO[GenreSortColumnType]


class SearchGenreResponseDTO(BaseDTO):
    genres: list[GenreItemDTO]
    total: int


class UpdateGenreCommandDTO(BaseDTO):
    genre_uuid: UUID
    name: str | None = None
    description: str | None = None


class DeleteGenreCommandDTO(BaseDTO):
    genre_uuid: UUID
