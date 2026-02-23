from uuid import UUID

from archipy.models.errors import AlreadyExistsError, NotFoundError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from src.configs.containers import ServiceContainer
from src.logics.rating.rating_logic import RatingLogic
from src.models.dtos.rating.domain.v1.rating_domain_interface_dtos import (
    RateMovieInputDTOV1,
    RateMovieOutputDTOV1,
    RateMovieRestInputDTOV1,
    UpdateRatingInputDTOV1,
    UpdateRatingRestInputDTOV1,
)
from src.utils.auth_dependencies import get_current_user_uuid
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
