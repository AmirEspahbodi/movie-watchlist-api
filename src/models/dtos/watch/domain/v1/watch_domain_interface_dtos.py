# src/models/dtos/watch/domain/v1/watch_domain_interface_dtos.py
from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict

from src.models.types.watch_sort_type import WatchSortColumnType
from src.models.types.watch_status_type import WatchStatusType


class WatchMovieRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID
    status: WatchStatusType = WatchStatusType.WANT_TO_WATCH


class WatchMovieInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID
    user_uuid: UUID
    status: WatchStatusType = WatchStatusType.WANT_TO_WATCH


class WatchMovieOutputDTOV1(BaseDTO):
    watch_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    status: WatchStatusType
    created_at: datetime
    updated_at: datetime


class WatchedMovieItemDTOV1(BaseDTO):
    watch_uuid: UUID
    movie_uuid: UUID
    title: str
    description: str | None = None
    genre_uuid: UUID
    status: WatchStatusType
    watched_at: datetime


class WatcherUserItemDTOV1(BaseDTO):
    watch_uuid: UUID
    user_uuid: UUID
    first_name: str
    last_name: str
    email: str
    status: WatchStatusType
    watched_at: datetime


class GetMyWatchHistoryInputDTOV1(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[WatchSortColumnType]
    status_filter: WatchStatusType | None = None

    @classmethod
    def create(
        cls,
        user_uuid: UUID,
        page: int = 1,
        page_size: int = 10,
        sort_column: WatchSortColumnType = WatchSortColumnType.CREATED_AT,
        sort_order: str = "desc",
        status_filter: WatchStatusType | None = None,
    ) -> "GetMyWatchHistoryInputDTOV1":
        return cls(
            user_uuid=user_uuid,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[WatchSortColumnType](column=sort_column, order=sort_order),
            status_filter=status_filter,
        )


class GetMyWatchHistoryOutputDTOV1(BaseDTO):
    watches: list[WatchedMovieItemDTOV1]
    total: int


class GetUserWatchHistoryInputDTOV1(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[WatchSortColumnType]
    status_filter: WatchStatusType | None = None

    @classmethod
    def create(
        cls,
        user_uuid: UUID,
        page: int = 1,
        page_size: int = 10,
        sort_column: WatchSortColumnType = WatchSortColumnType.CREATED_AT,
        sort_order: str = "desc",
        status_filter: WatchStatusType | None = None,
    ) -> "GetUserWatchHistoryInputDTOV1":
        return cls(
            user_uuid=user_uuid,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[WatchSortColumnType](column=sort_column, order=sort_order),
            status_filter=status_filter,
        )


class GetUserWatchHistoryOutputDTOV1(BaseDTO):
    watches: list[WatchedMovieItemDTOV1]
    total: int


class GetMovieWatchersInputDTOV1(BaseDTO):
    movie_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[WatchSortColumnType]
    status_filter: WatchStatusType | None = None

    @classmethod
    def create(
        cls,
        movie_uuid: UUID,
        page: int = 1,
        page_size: int = 10,
        sort_column: WatchSortColumnType = WatchSortColumnType.CREATED_AT,
        sort_order: str = "desc",
        status_filter: WatchStatusType | None = None,
    ) -> "GetMovieWatchersInputDTOV1":
        return cls(
            movie_uuid=movie_uuid,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[WatchSortColumnType](column=sort_column, order=sort_order),
            status_filter=status_filter,
        )


class GetMovieWatchersOutputDTOV1(BaseDTO):
    watchers: list[WatcherUserItemDTOV1]
    total: int


class UpdateWatchStatusRestInputDTOV1(BaseDTO):
    status: WatchStatusType


class UpdateWatchStatusInputDTOV1(BaseDTO):
    watch_uuid: UUID
    user_uuid: UUID
    status: WatchStatusType


class DeleteWatchInputDTOV1(BaseDTO):
    """Domain input for deleting a watch entry owned by the authenticated user."""

    user_uuid: UUID
    movie_uuid: UUID
