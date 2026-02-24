from uuid import UUID

from archipy.models.errors import AlreadyExistsError, NotFoundError, PermissionDeniedError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.configs.containers import ServiceContainer
from src.logics.movie.movie_logic import MovieLogic
from src.models.dtos.movie.domain.v1.movie_domain_interface_dtos import (
    BulkCreateMovieInputDTOV1,
    BulkCreateMovieOutputDTOV1,
    BulkCreateMovieRestInputDTOV1,
    CreateMovieInputDTOV1,
    CreateMovieOutputDTOV1,
    CreateMovieRestInputDTOV1,
    DeleteMovieInputDTOV1,
    GetMovieInputDTOV1,
    GetMovieOutputDTOV1,
    SearchMovieInputDTOV1,
    SearchMovieOutputDTOV1,
    UpdateMovieInputDTOV1,
    UpdateMovieRestInputDTOV1,
)
from src.models.types.api_router_type import ApiRouterType
from src.models.types.movie_sort_type import MovieSortColumnType
from src.utils.auth_dependencies import get_current_admin_user_uuid, get_current_user_uuid
from src.utils.utils import Utils

routerV1: APIRouter = APIRouter(tags=[ApiRouterType.MOVIE])

_ADMIN_AUTH_RESPONSES = Utils.get_fastapi_exception_responses(
    [UnauthenticatedError, PermissionDeniedError],
)


@routerV1.post(
    path="/",
    response_model=CreateMovieOutputDTOV1,
    status_code=status.HTTP_201_CREATED,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def create_movie(
    input_dto: CreateMovieRestInputDTOV1,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    movie_logic: MovieLogic = Depends(Provide[ServiceContainer.movie_logic]),
) -> CreateMovieOutputDTOV1:
    logic_dto = CreateMovieInputDTOV1(
        title=input_dto.title,
        description=input_dto.description,
        genre_uuid=input_dto.genre_uuid,
    )
    return await movie_logic.create_movie(input_dto=logic_dto)


@routerV1.post(
    path="/bulk",
    response_model=BulkCreateMovieOutputDTOV1,
    status_code=status.HTTP_201_CREATED,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def bulk_create_movies(
    input_dto: BulkCreateMovieRestInputDTOV1,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    movie_logic: MovieLogic = Depends(Provide[ServiceContainer.movie_logic]),
) -> BulkCreateMovieOutputDTOV1:
    logic_dto = BulkCreateMovieInputDTOV1(
        movies=[
            CreateMovieInputDTOV1(title=m.title, description=m.description, genre_uuid=m.genre_uuid)
            for m in input_dto.movies
        ]
    )
    return await movie_logic.bulk_create_movie(input_dto=logic_dto)


@routerV1.get(
    path="/",
    response_model=SearchMovieOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=_ADMIN_AUTH_RESPONSES,
)
@inject
async def search_movies(
    _admin_uuid: UUID = Depends(get_current_user_uuid),
    title: str | None = None,
    genre_uuid: UUID | None = None,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    sort_column: MovieSortColumnType = Query(default=MovieSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    movie_logic: MovieLogic = Depends(Provide[ServiceContainer.movie_logic]),
) -> SearchMovieOutputDTOV1:
    input_dto = SearchMovieInputDTOV1.create(
        title=title,
        genre_uuid=genre_uuid,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )
    return await movie_logic.search_movies(input_dto=input_dto)


@routerV1.get(
    path="/{movie_uuid}",
    response_model=GetMovieOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def get_movie(
    movie_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_user_uuid),
    movie_logic: MovieLogic = Depends(Provide[ServiceContainer.movie_logic]),
) -> GetMovieOutputDTOV1:
    input_dto = GetMovieInputDTOV1(movie_uuid=movie_uuid)
    return await movie_logic.get_movie(input_dto=input_dto)


@routerV1.patch(
    path="/{movie_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def update_movie(
    movie_uuid: UUID,
    input_dto: UpdateMovieRestInputDTOV1,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    movie_logic: MovieLogic = Depends(Provide[ServiceContainer.movie_logic]),
) -> Response:
    update_dto = UpdateMovieInputDTOV1(movie_uuid=movie_uuid, **input_dto.model_dump())
    await movie_logic.update_movie(input_dto=update_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@routerV1.delete(
    path="/{movie_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def delete_movie(
    movie_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    movie_logic: MovieLogic = Depends(Provide[ServiceContainer.movie_logic]),
) -> Response:
    input_dto = DeleteMovieInputDTOV1(movie_uuid=movie_uuid)
    await movie_logic.delete_movie(input_dto=input_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
