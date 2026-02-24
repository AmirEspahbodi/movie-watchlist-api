# src/repositories/watch/watch_repository.py
from src.models.dtos.watch.repository.watch_repository_interface_dtos import (
    CheckWatchedQueryDTO,
    CheckWatchExistsQueryDTO,
    CreateWatchCommandDTO,
    CreateWatchResponseDTO,
    DeleteWatchCommandDTO,
    GetMovieWatchersQueryDTO,
    GetMovieWatchersResponseDTO,
    GetUserWatchHistoryQueryDTO,
    GetUserWatchHistoryResponseDTO,
    UpdateWatchStatusCommandDTO,
)
from src.repositories.watch.adapters.watch_postgres_adapter import WatchPostgresAdapter


class WatchRepository:
    def __init__(self, postgres_adapter: WatchPostgresAdapter) -> None:
        self._postgres_adapter = postgres_adapter

    async def check_watch_exists(self, input_dto: CheckWatchExistsQueryDTO) -> bool:
        return await self._postgres_adapter.check_watch_exists(input_dto=input_dto)

    async def check_movie_watched(self, input_dto: CheckWatchedQueryDTO) -> bool:
        """Delegate the WATCHED-status existence check to the postgres adapter."""
        return await self._postgres_adapter.check_movie_watched(input_dto=input_dto)

    async def create_watch(self, input_dto: CreateWatchCommandDTO) -> CreateWatchResponseDTO:
        return await self._postgres_adapter.create_watch(input_dto=input_dto)

    async def get_user_watch_history(
        self,
        input_dto: GetUserWatchHistoryQueryDTO,
    ) -> GetUserWatchHistoryResponseDTO:
        return await self._postgres_adapter.get_user_watch_history(input_dto=input_dto)

    async def get_movie_watchers(
        self,
        input_dto: GetMovieWatchersQueryDTO,
    ) -> GetMovieWatchersResponseDTO:
        return await self._postgres_adapter.get_movie_watchers(input_dto=input_dto)

    async def update_watch_status(self, input_dto: UpdateWatchStatusCommandDTO) -> None:
        await self._postgres_adapter.update_watch_status(input_dto=input_dto)

    async def delete_watch(self, input_dto: DeleteWatchCommandDTO) -> None:
        await self._postgres_adapter.delete_watch(input_dto=input_dto)
