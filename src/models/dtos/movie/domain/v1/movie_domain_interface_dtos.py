from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict, Field

from src.models.types.movie_sort_type import MovieSortColumnType


class CreateMovieRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    genre_uuid: UUID


class CreateMovieInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str | None = None
    genre_uuid: UUID


class CreateMovieOutputDTOV1(BaseDTO):
    movie_uuid: UUID
    title: str
    description: str | None = None
    genre_uuid: UUID
    created_at: datetime
    updated_at: datetime


class BulkCreateMovieRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movies: list[CreateMovieRestInputDTOV1] = Field(..., min_length=1, max_length=100)


class BulkCreateMovieInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movies: list[CreateMovieInputDTOV1]


class BulkCreateMovieOutputDTOV1(BaseDTO):
    movies: list[CreateMovieOutputDTOV1]


class GetMovieInputDTOV1(BaseDTO):
    movie_uuid: UUID


class GetMovieOutputDTOV1(BaseDTO):
    movie_uuid: UUID
    title: str
    description: str | None = None
    genre_uuid: UUID
    created_at: datetime
    updated_at: datetime


class MovieItemDTOV1(BaseDTO):
    movie_uuid: UUID
    title: str
    description: str | None = None
    genre_uuid: UUID
    created_at: datetime


class SearchMovieInputDTOV1(BaseDTO):
    title: str | None = None
    genre_uuid: UUID | None = None
    pagination: PaginationDTO
    sort_info: SortDTO[MovieSortColumnType]

    @classmethod
    def create(
        cls,
        title: str | None = None,
        genre_uuid: UUID | None = None,
        page: int = 1,
        page_size: int = 10,
        sort_column: MovieSortColumnType = MovieSortColumnType.CREATED_AT,
        sort_order: str = "desc",
    ) -> "SearchMovieInputDTOV1":
        return cls(
            title=title,
            genre_uuid=genre_uuid,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[MovieSortColumnType](column=sort_column, order=sort_order),
        )


class SearchMovieOutputDTOV1(BaseDTO):
    movies: list[MovieItemDTOV1]
    total: int


class UpdateMovieRestInputDTOV1(BaseDTO):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    genre_uuid: UUID | None = None


class UpdateMovieInputDTOV1(UpdateMovieRestInputDTOV1):
    movie_uuid: UUID


class DeleteMovieInputDTOV1(BaseDTO):
    movie_uuid: UUID
