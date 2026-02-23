from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator
from archipy.models.errors import AlreadyExistsError

from src.models.dtos.watch.domain.v1.watch_domain_interface_dtos import (
    WatchMovieInputDTOV1,
    WatchMovieOutputDTOV1,
)
from src.models.dtos.watch.repository.watch_repository_interface_dtos import (
    CheckWatchExistsQueryDTO,
    CreateWatchCommandDTO,
)
from src.repositories.watch.watch_repository import WatchRepository


class WatchLogic:
    def __init__(self, repository: WatchRepository) -> None:
        self._repository = repository

    @async_postgres_sqlalchemy_atomic_decorator
    async def watch_movie(self, input_dto: WatchMovieInputDTOV1) -> WatchMovieOutputDTOV1:
        exists_query = CheckWatchExistsQueryDTO(
            user_uuid=input_dto.user_uuid,
            movie_uuid=input_dto.movie_uuid,
        )
        already_watched = await self._repository.check_watch_exists(input_dto=exists_query)
        if already_watched:
            raise AlreadyExistsError(resource_type="UserWatchMovieEntity")

        command = CreateWatchCommandDTO(
            user_uuid=input_dto.user_uuid,
            movie_uuid=input_dto.movie_uuid,
        )
        response = await self._repository.create_watch(input_dto=command)
        return WatchMovieOutputDTOV1.model_validate(obj=response)
