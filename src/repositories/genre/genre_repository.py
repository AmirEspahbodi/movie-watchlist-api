from src.models.dtos.genre.repository.genre_repository_interface_dtos import (
    BulkCreateGenreCommandDTO,
    BulkCreateGenreResponseDTO,
    CreateGenreCommandDTO,
    CreateGenreResponseDTO,
    DeleteGenreCommandDTO,
    GetGenreQueryDTO,
    GetGenreResponseDTO,
    SearchGenreQueryDTO,
    SearchGenreResponseDTO,
    UpdateGenreCommandDTO,
)
from src.repositories.genre.adapters.genre_postgres_adapter import GenrePostgresAdapter


class GenreRepository:
    def __init__(self, postgres_adapter: GenrePostgresAdapter) -> None:
        self._postgres_adapter: GenrePostgresAdapter = postgres_adapter

    async def create_genre(self, input_dto: CreateGenreCommandDTO) -> CreateGenreResponseDTO:
        return await self._postgres_adapter.create_genre(input_dto=input_dto)

    async def bulk_create_genre(self, input_dto: BulkCreateGenreCommandDTO) -> BulkCreateGenreResponseDTO:
        return await self._postgres_adapter.bulk_create_genre(input_dto=input_dto)

    async def get_genre(self, input_dto: GetGenreQueryDTO) -> GetGenreResponseDTO:
        return await self._postgres_adapter.get_genre(input_dto=input_dto)

    async def search_genres(self, input_dto: SearchGenreQueryDTO) -> SearchGenreResponseDTO:
        return await self._postgres_adapter.search_genres(input_dto=input_dto)

    async def update_genre(self, input_dto: UpdateGenreCommandDTO) -> None:
        await self._postgres_adapter.update_genre(input_dto=input_dto)

    async def delete_genre(self, input_dto: DeleteGenreCommandDTO) -> None:
        await self._postgres_adapter.delete_genre(input_dto=input_dto)
