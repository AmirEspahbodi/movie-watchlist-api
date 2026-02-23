from uuid import UUID

from archipy.models.errors import AlreadyExistsError, NotFoundError, PermissionDeniedError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.configs.containers import ServiceContainer
from src.logics.rating.rating_logic import RatingLogic
from src.models.dtos.rating.domain.v1.rating_domain_interface_dtos import (
    GetMovieRatersInputDTOV1,
    GetMovieRatersOutputDTOV1,
    GetMyRatingsInputDTOV1,
    GetMyRatingsOutputDTOV1,
    GetUserRatingsInputDTOV1,
    GetUserRatingsOutputDTOV1,
    RateMovieInputDTOV1,
    RateMovieOutputDTOV1,
    RateMovieRestInputDTOV1,
    UpdateRatingInputDTOV1,
    UpdateRatingRestInputDTOV1,
)
from src.models.types.rating_sort_type import RatingSortColumnType
from src.utils.auth_dependencies import get_current_admin_user_uuid, get_current_user_uuid
from src.utils.utils import Utils

routerV1 = APIRouter(tags=["⭐️ RATINGS"])


@routerV1.post(
    path="/",
    response_model=RateMovieOutputDTOV1,
    status_code=status.HTTP_201_CREATED,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError, UnauthenticatedError]),
)
@inject
async def rate_movie(
    request: RateMovieRestInputDTOV1,
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    rating_logic: RatingLogic = Depends(Provide[ServiceContainer.rating_logic]),
) -> RateMovieOutputDTOV1:
    logic_dto = RateMovieInputDTOV1(
        movie_uuid=request.movie_uuid,
        user_uuid=current_user_uuid,
        score=request.score,
    )
    return await rating_logic.rate_movie(input_dto=logic_dto)


@routerV1.patch(
    path="/{rate_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError, UnauthenticatedError]),
)
@inject
async def update_rating(
    rate_uuid: UUID,
    request: UpdateRatingRestInputDTOV1,
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    rating_logic: RatingLogic = Depends(Provide[ServiceContainer.rating_logic]),
) -> Response:
    logic_dto = UpdateRatingInputDTOV1(
        rate_uuid=rate_uuid,
        user_uuid=current_user_uuid,
        score=request.score,
    )
    await rating_logic.update_rating(input_dto=logic_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@routerV1.get(
    path="/my-ratings",
    response_model=GetMyRatingsOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([UnauthenticatedError]),
)
@inject
async def get_my_ratings(
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_column: RatingSortColumnType = Query(default=RatingSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    rating_logic: RatingLogic = Depends(Provide[ServiceContainer.rating_logic]),
) -> GetMyRatingsOutputDTOV1:
    input_dto = GetMyRatingsInputDTOV1.create(
        user_uuid=current_user_uuid,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )
    return await rating_logic.get_my_ratings(input_dto=input_dto)


@routerV1.get(
    path="/user/{user_uuid}",
    response_model=GetUserRatingsOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([UnauthenticatedError, PermissionDeniedError, NotFoundError]),
)
@inject
async def get_user_ratings(
    user_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_column: RatingSortColumnType = Query(default=RatingSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    rating_logic: RatingLogic = Depends(Provide[ServiceContainer.rating_logic]),
) -> GetUserRatingsOutputDTOV1:
    input_dto = GetUserRatingsInputDTOV1.create(
        user_uuid=user_uuid,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )
    return await rating_logic.get_user_ratings(input_dto=input_dto)


@routerV1.get(
    path="/movie/{movie_uuid}/raters",
    response_model=GetMovieRatersOutputDTOV1,
    status_code=status.HTTP_200_OK,
    responses=Utils.get_fastapi_exception_responses([UnauthenticatedError, PermissionDeniedError, NotFoundError]),
)
@inject
async def get_movie_raters(
    movie_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_column: RatingSortColumnType = Query(default=RatingSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    rating_logic: RatingLogic = Depends(Provide[ServiceContainer.rating_logic]),
) -> GetMovieRatersOutputDTOV1:
    input_dto = GetMovieRatersInputDTOV1.create(
        movie_uuid=movie_uuid,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )
    return await rating_logic.get_movie_raters(input_dto=input_dto)
