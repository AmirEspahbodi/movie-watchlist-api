# src/controllers/watch/v1/watch_controller.py
from uuid import UUID

from archipy.models.errors import (
    AlreadyExistsError,
    InvalidArgumentError,
    NotFoundError,
    PermissionDeniedError,
    UnauthenticatedError,
)
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.configs.containers import ServiceContainer
from src.logics.watch.watch_logic import WatchLogic
from src.models.dtos.watch.domain.v1.watch_domain_interface_dtos import (
    DeleteWatchInputDTOV1,
    GetMovieWatchersInputDTOV1,
    GetMovieWatchersOutputDTOV1,
    GetMyWatchHistoryInputDTOV1,
    GetMyWatchHistoryOutputDTOV1,
    GetUserWatchHistoryInputDTOV1,
    GetUserWatchHistoryOutputDTOV1,
    UpdateWatchStatusInputDTOV1,
    UpdateWatchStatusRestInputDTOV1,
    WatchMovieInputDTOV1,
    WatchMovieOutputDTOV1,
    WatchMovieRestInputDTOV1,
)
from src.models.types.watch_sort_type import WatchSortColumnType
from src.models.types.watch_status_type import WatchStatusType
from src.utils.auth_dependencies import get_current_admin_user_uuid, get_current_user_uuid
from src.utils.utils import Utils

routerV1 = APIRouter(tags=["🎬 WATCHLIST"])


@routerV1.post(
    path="/",
    response_model=WatchMovieOutputDTOV1,
    status_code=status.HTTP_201_CREATED,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError, UnauthenticatedError]),
)
@inject
async def watch_movie(
    request: WatchMovieRestInputDTOV1,
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    watch_logic: WatchLogic = Depends(Provide[ServiceContainer.watch_logic]),
) -> WatchMovieOutputDTOV1:
    logic_dto = WatchMovieInputDTOV1(
        movie_uuid=request.movie_uuid,
        user_uuid=current_user_uuid,
        status=request.status,
    )
    return await watch_logic.watch_movie(input_dto=logic_dto)


@routerV1.get(
    path="/my-history",
    response_model=GetMyWatchHistoryOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([UnauthenticatedError]),
)
@inject
async def get_my_watch_history(
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_column: WatchSortColumnType = Query(default=WatchSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    status_filter: WatchStatusType | None = Query(default=None),
    watch_logic: WatchLogic = Depends(Provide[ServiceContainer.watch_logic]),
) -> GetMyWatchHistoryOutputDTOV1:
    input_dto = GetMyWatchHistoryInputDTOV1.create(
        user_uuid=current_user_uuid,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
        status_filter=status_filter,
    )
    return await watch_logic.get_my_watch_history(input_dto=input_dto)


@routerV1.get(
    path="/user/{user_uuid}",
    response_model=GetUserWatchHistoryOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([UnauthenticatedError, PermissionDeniedError, NotFoundError]),
)
@inject
async def get_user_watch_history(
    user_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_column: WatchSortColumnType = Query(default=WatchSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    status_filter: WatchStatusType | None = Query(default=None),
    watch_logic: WatchLogic = Depends(Provide[ServiceContainer.watch_logic]),
) -> GetUserWatchHistoryOutputDTOV1:
    input_dto = GetUserWatchHistoryInputDTOV1.create(
        user_uuid=user_uuid,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
        status_filter=status_filter,
    )
    return await watch_logic.get_user_watch_history(input_dto=input_dto)


@routerV1.get(
    path="/movie/{movie_uuid}/watchers",
    response_model=GetMovieWatchersOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([UnauthenticatedError, PermissionDeniedError, NotFoundError]),
)
@inject
async def get_movie_watchers(
    movie_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_column: WatchSortColumnType = Query(default=WatchSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    status_filter: WatchStatusType | None = Query(default=None),
    watch_logic: WatchLogic = Depends(Provide[ServiceContainer.watch_logic]),
) -> GetMovieWatchersOutputDTOV1:
    input_dto = GetMovieWatchersInputDTOV1.create(
        movie_uuid=movie_uuid,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
        status_filter=status_filter,
    )
    return await watch_logic.get_movie_watchers(input_dto=input_dto)


@routerV1.patch(
    path="/{watch_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError, UnauthenticatedError]),
)
@inject
async def update_watch_status(
    watch_uuid: UUID,
    request: UpdateWatchStatusRestInputDTOV1,
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    watch_logic: WatchLogic = Depends(Provide[ServiceContainer.watch_logic]),
) -> Response:
    logic_dto = UpdateWatchStatusInputDTOV1(
        watch_uuid=watch_uuid,
        user_uuid=current_user_uuid,
        status=request.status,
    )
    await watch_logic.update_watch_status(input_dto=logic_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@routerV1.delete(
    path="/movie/{movie_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError, InvalidArgumentError, UnauthenticatedError]),
)
@inject
async def delete_watch(
    movie_uuid: UUID,
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    watch_logic: WatchLogic = Depends(Provide[ServiceContainer.watch_logic]),
) -> Response:
    logic_dto = DeleteWatchInputDTOV1(
        user_uuid=current_user_uuid,
        movie_uuid=movie_uuid,
    )
    await watch_logic.delete_watch(input_dto=logic_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
