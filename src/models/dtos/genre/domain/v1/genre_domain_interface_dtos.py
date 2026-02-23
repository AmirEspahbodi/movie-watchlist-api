from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict, Field

from src.models.types.genre_sort_type import GenreSortColumnType


class CreateGenreRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)


class CreateGenreInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None


class CreateGenreOutputDTOV1(BaseDTO):
    genre_uuid: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class BulkCreateGenreRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    genres: list[CreateGenreRestInputDTOV1] = Field(..., min_length=1, max_length=100)


class BulkCreateGenreInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    genres: list[CreateGenreInputDTOV1]


class BulkCreateGenreOutputDTOV1(BaseDTO):
    genres: list[CreateGenreOutputDTOV1]


class GetGenreInputDTOV1(BaseDTO):
    genre_uuid: UUID


class GetGenreOutputDTOV1(BaseDTO):
    genre_uuid: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class GenreItemDTOV1(BaseDTO):
    genre_uuid: UUID
    name: str
    description: str | None = None
    created_at: datetime


class SearchGenreInputDTOV1(BaseDTO):
    name: str | None = None
    pagination: PaginationDTO
    sort_info: SortDTO[GenreSortColumnType]

    @classmethod
    def create(
        cls,
        name: str | None = None,
        page: int = 1,
        page_size: int = 10,
        sort_column: GenreSortColumnType = GenreSortColumnType.CREATED_AT,
        sort_order: str = "desc",
    ) -> "SearchGenreInputDTOV1":
        return cls(
            name=name,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[GenreSortColumnType](column=sort_column, order=sort_order),
        )


class SearchGenreOutputDTOV1(BaseDTO):
    genres: list[GenreItemDTOV1]
    total: int


class UpdateGenreRestInputDTOV1(BaseDTO):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)


class UpdateGenreInputDTOV1(UpdateGenreRestInputDTOV1):
    genre_uuid: UUID


class DeleteGenreInputDTOV1(BaseDTO):
    genre_uuid: UUID
