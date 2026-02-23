from src.models.dtos.rating.repository.rating_repository_interface_dtos import (
    CheckRatingExistsQueryDTO,
    CreateRatingCommandDTO,
    CreateRatingResponseDTO,
    UpdateRatingCommandDTO,
)
from src.repositories.rating.adapters.rating_postgres_adapter import RatingPostgresAdapter


class RatingRepository:
    def __init__(self, postgres_adapter: RatingPostgresAdapter) -> None:
        self._postgres_adapter = postgres_adapter

    async def check_rating_exists(self, input_dto: CheckRatingExistsQueryDTO) -> bool:
        return await self._postgres_adapter.check_rating_exists(input_dto=input_dto)

    async def create_rating(self, input_dto: CreateRatingCommandDTO) -> CreateRatingResponseDTO:
        return await self._postgres_adapter.create_rating(input_dto=input_dto)

    async def update_rating(self, input_dto: UpdateRatingCommandDTO) -> None:
        await self._postgres_adapter.update_rating(input_dto=input_dto)
