from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict

from src.models.types.watch_sort_type import WatchSortColumnType


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


class WatchedMovieItemDTO(BaseModel):
    """One row returned when listing a user's watched movies."""

    model_config = ConfigDict(from_attributes=True)

    watch_uuid: UUID
    movie_uuid: UUID
    title: str
    description: str | None
    genre_uuid: UUID
    watched_at: datetime


class GetUserWatchHistoryQueryDTO(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[WatchSortColumnType]


class GetUserWatchHistoryResponseDTO(BaseDTO):
    watches: list[WatchedMovieItemDTO]
    total: int


class WatcherUserItemDTO(BaseModel):
    """One row returned when listing users who watched a movie."""

    model_config = ConfigDict(from_attributes=True)

    watch_uuid: UUID
    user_uuid: UUID
    first_name: str
    last_name: str
    email: str
    watched_at: datetime


class GetMovieWatchersQueryDTO(BaseDTO):
    movie_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[WatchSortColumnType]


class GetMovieWatchersResponseDTO(BaseDTO):
    watchers: list[WatcherUserItemDTO]
    total: int
