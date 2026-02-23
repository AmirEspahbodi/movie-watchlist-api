from src.models.dtos.watch.repository.watch_repository_interface_dtos import (
    CheckWatchExistsQueryDTO,
    CreateWatchCommandDTO,
    CreateWatchResponseDTO,
)
from src.repositories.watch.adapters.watch_postgres_adapter import WatchPostgresAdapter


class WatchRepository:
    def __init__(self, postgres_adapter: WatchPostgresAdapter) -> None:
        self._postgres_adapter = postgres_adapter

    async def check_watch_exists(self, input_dto: CheckWatchExistsQueryDTO) -> bool:
        return await self._postgres_adapter.check_watch_exists(input_dto=input_dto)

    async def create_watch(self, input_dto: CreateWatchCommandDTO) -> CreateWatchResponseDTO:
        return await self._postgres_adapter.create_watch(input_dto=input_dto)
