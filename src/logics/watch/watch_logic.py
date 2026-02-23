from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator
from archipy.models.errors import AlreadyExistsError

from src.models.dtos.watch.domain.v1.watch_domain_interface_dtos import (
    GetMovieWatchersInputDTOV1,
    GetMovieWatchersOutputDTOV1,
    GetMyWatchHistoryInputDTOV1,
    GetMyWatchHistoryOutputDTOV1,
    GetUserWatchHistoryInputDTOV1,
    GetUserWatchHistoryOutputDTOV1,
    WatchedMovieItemDTOV1,
    WatcherUserItemDTOV1,
    WatchMovieInputDTOV1,
    WatchMovieOutputDTOV1,
)
from src.models.dtos.watch.repository.watch_repository_interface_dtos import (
    CheckWatchExistsQueryDTO,
    CreateWatchCommandDTO,
    GetMovieWatchersQueryDTO,
    GetUserWatchHistoryQueryDTO,
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

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_my_watch_history(
        self,
        input_dto: GetMyWatchHistoryInputDTOV1,
    ) -> GetMyWatchHistoryOutputDTOV1:
        query = GetUserWatchHistoryQueryDTO(
            user_uuid=input_dto.user_uuid,
            pagination=input_dto.pagination,
            sort_info=input_dto.sort_info,
        )
        response = await self._repository.get_user_watch_history(input_dto=query)
        return GetMyWatchHistoryOutputDTOV1(
            watches=[
                WatchedMovieItemDTOV1(
                    watch_uuid=w.watch_uuid,
                    movie_uuid=w.movie_uuid,
                    title=w.title,
                    description=w.description,
                    genre_uuid=w.genre_uuid,
                    watched_at=w.watched_at,
                )
                for w in response.watches
            ],
            total=response.total,
        )

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_user_watch_history(
        self,
        input_dto: GetUserWatchHistoryInputDTOV1,
    ) -> GetUserWatchHistoryOutputDTOV1:
        query = GetUserWatchHistoryQueryDTO(
            user_uuid=input_dto.user_uuid,
            pagination=input_dto.pagination,
            sort_info=input_dto.sort_info,
        )
        response = await self._repository.get_user_watch_history(input_dto=query)
        return GetUserWatchHistoryOutputDTOV1(
            watches=[
                WatchedMovieItemDTOV1(
                    watch_uuid=w.watch_uuid,
                    movie_uuid=w.movie_uuid,
                    title=w.title,
                    description=w.description,
                    genre_uuid=w.genre_uuid,
                    watched_at=w.watched_at,
                )
                for w in response.watches
            ],
            total=response.total,
        )

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_movie_watchers(
        self,
        input_dto: GetMovieWatchersInputDTOV1,
    ) -> GetMovieWatchersOutputDTOV1:
        query = GetMovieWatchersQueryDTO(
            movie_uuid=input_dto.movie_uuid,
            pagination=input_dto.pagination,
            sort_info=input_dto.sort_info,
        )
        response = await self._repository.get_movie_watchers(input_dto=query)
        return GetMovieWatchersOutputDTOV1(
            watchers=[
                WatcherUserItemDTOV1(
                    watch_uuid=u.watch_uuid,
                    user_uuid=u.user_uuid,
                    first_name=u.first_name,
                    last_name=u.last_name,
                    email=u.email,
                    watched_at=u.watched_at,
                )
                for u in response.watchers
            ],
            total=response.total,
        )
