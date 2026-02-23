from uuid import UUID

from archipy.models.errors import AlreadyExistsError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.configs.containers import ServiceContainer
from src.logics.watch.watch_logic import WatchLogic
from src.models.dtos.watch.domain.v1.watch_domain_interface_dtos import (
    WatchMovieInputDTOV1,
    WatchMovieOutputDTOV1,
    WatchMovieRestInputDTOV1,
)
from src.utils.auth_dependencies import get_current_user_uuid
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
    )
    return await watch_logic.watch_movie(input_dto=logic_dto)
