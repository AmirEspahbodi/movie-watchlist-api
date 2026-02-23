from uuid import UUID

from archipy.models.errors import AlreadyExistsError, NotFoundError, PermissionDeniedError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.configs.containers import ServiceContainer
from src.logics.genre.genre_logic import GenreLogic
from src.models.dtos.genre.domain.v1.genre_domain_interface_dtos import (
    BulkCreateGenreInputDTOV1,
    BulkCreateGenreOutputDTOV1,
    BulkCreateGenreRestInputDTOV1,
    CreateGenreInputDTOV1,
    CreateGenreOutputDTOV1,
    CreateGenreRestInputDTOV1,
    DeleteGenreInputDTOV1,
    GetGenreInputDTOV1,
    GetGenreOutputDTOV1,
    SearchGenreInputDTOV1,
    SearchGenreOutputDTOV1,
    UpdateGenreInputDTOV1,
    UpdateGenreRestInputDTOV1,
)
from src.models.types.api_router_type import ApiRouterType
from src.models.types.genre_sort_type import GenreSortColumnType
from src.utils.auth_dependencies import get_current_admin_user_uuid
from src.utils.utils import Utils

routerV1: APIRouter = APIRouter(tags=[ApiRouterType.GENRE])

_ADMIN_AUTH_RESPONSES = Utils.get_fastapi_exception_responses(
    [UnauthenticatedError, PermissionDeniedError],
)


@routerV1.post(
    path="/",
    response_model=CreateGenreOutputDTOV1,
    status_code=status.HTTP_201_CREATED,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def create_genre(
    input_dto: CreateGenreRestInputDTOV1,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    genre_logic: GenreLogic = Depends(Provide[ServiceContainer.genre_logic]),
) -> CreateGenreOutputDTOV1:
    logic_dto = CreateGenreInputDTOV1(name=input_dto.name, description=input_dto.description)
    return await genre_logic.create_genre(input_dto=logic_dto)


@routerV1.post(
    path="/bulk",
    response_model=BulkCreateGenreOutputDTOV1,
    status_code=status.HTTP_201_CREATED,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def bulk_create_genres(
    input_dto: BulkCreateGenreRestInputDTOV1,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    genre_logic: GenreLogic = Depends(Provide[ServiceContainer.genre_logic]),
) -> BulkCreateGenreOutputDTOV1:
    logic_dto = BulkCreateGenreInputDTOV1(
        genres=[CreateGenreInputDTOV1(name=g.name, description=g.description) for g in input_dto.genres]
    )
    return await genre_logic.bulk_create_genre(input_dto=logic_dto)


@routerV1.get(
    path="/",
    response_model=SearchGenreOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=_ADMIN_AUTH_RESPONSES,
)
@inject
async def search_genres(
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    name: str | None = None,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    sort_column: GenreSortColumnType = Query(default=GenreSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    genre_logic: GenreLogic = Depends(Provide[ServiceContainer.genre_logic]),
) -> SearchGenreOutputDTOV1:
    input_dto = SearchGenreInputDTOV1.create(
        name=name,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )
    return await genre_logic.search_genres(input_dto=input_dto)


@routerV1.get(
    path="/{genre_uuid}",
    response_model=GetGenreOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def get_genre(
    genre_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    genre_logic: GenreLogic = Depends(Provide[ServiceContainer.genre_logic]),
) -> GetGenreOutputDTOV1:
    input_dto = GetGenreInputDTOV1(genre_uuid=genre_uuid)
    return await genre_logic.get_genre(input_dto=input_dto)


@routerV1.patch(
    path="/{genre_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def update_genre(
    genre_uuid: UUID,
    input_dto: UpdateGenreRestInputDTOV1,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    genre_logic: GenreLogic = Depends(Provide[ServiceContainer.genre_logic]),
) -> Response:
    update_dto = UpdateGenreInputDTOV1(genre_uuid=genre_uuid, **input_dto.model_dump())
    await genre_logic.update_genre(input_dto=update_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@routerV1.delete(
    path="/{genre_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def delete_genre(
    genre_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    genre_logic: GenreLogic = Depends(Provide[ServiceContainer.genre_logic]),
) -> Response:
    input_dto = DeleteGenreInputDTOV1(genre_uuid=genre_uuid)
    await genre_logic.delete_genre(input_dto=input_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
