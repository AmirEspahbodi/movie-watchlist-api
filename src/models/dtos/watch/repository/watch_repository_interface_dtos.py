# src/models/dtos/watch/repository/watch_repository_interface_dtos.py
from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict

from src.models.types.watch_sort_type import WatchSortColumnType
from src.models.types.watch_status_type import WatchStatusType


class CreateWatchCommandDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_uuid: UUID
    movie_uuid: UUID
    status: WatchStatusType = WatchStatusType.WANT_TO_WATCH


class CreateWatchResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    watch_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    status: WatchStatusType
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
    status: WatchStatusType
    watched_at: datetime


class GetUserWatchHistoryQueryDTO(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[WatchSortColumnType]
    status_filter: WatchStatusType | None = None


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
    status: WatchStatusType
    watched_at: datetime


class GetMovieWatchersQueryDTO(BaseDTO):
    movie_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[WatchSortColumnType]
    status_filter: WatchStatusType | None = None


class GetMovieWatchersResponseDTO(BaseDTO):
    watchers: list[WatcherUserItemDTO]
    total: int


class UpdateWatchStatusCommandDTO(BaseDTO):
    watch_uuid: UUID
    user_uuid: UUID
    status: WatchStatusType


class DeleteWatchCommandDTO(BaseDTO):
    """Command to delete a watch record — only permitted when status is WANT_TO_WATCH."""

    user_uuid: UUID
    movie_uuid: UUID
