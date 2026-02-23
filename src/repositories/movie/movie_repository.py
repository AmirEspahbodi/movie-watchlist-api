from src.models.dtos.movie.repository.movie_repository_interface_dtos import (
    BulkCreateMovieCommandDTO,
    BulkCreateMovieResponseDTO,
    CreateMovieCommandDTO,
    CreateMovieResponseDTO,
    DeleteMovieCommandDTO,
    GetMovieQueryDTO,
    GetMovieResponseDTO,
    SearchMovieQueryDTO,
    SearchMovieResponseDTO,
    UpdateMovieCommandDTO,
)
from src.repositories.movie.adapters.movie_postgres_adapter import MoviePostgresAdapter


class MovieRepository:
    def __init__(self, postgres_adapter: MoviePostgresAdapter) -> None:
        self._postgres_adapter: MoviePostgresAdapter = postgres_adapter

    async def create_movie(self, input_dto: CreateMovieCommandDTO) -> CreateMovieResponseDTO:
        return await self._postgres_adapter.create_movie(input_dto=input_dto)

    async def bulk_create_movie(self, input_dto: BulkCreateMovieCommandDTO) -> BulkCreateMovieResponseDTO:
        return await self._postgres_adapter.bulk_create_movie(input_dto=input_dto)

    async def get_movie(self, input_dto: GetMovieQueryDTO) -> GetMovieResponseDTO:
        return await self._postgres_adapter.get_movie(input_dto=input_dto)

    async def search_movies(self, input_dto: SearchMovieQueryDTO) -> SearchMovieResponseDTO:
        return await self._postgres_adapter.search_movies(input_dto=input_dto)

    async def update_movie(self, input_dto: UpdateMovieCommandDTO) -> None:
        await self._postgres_adapter.update_movie(input_dto=input_dto)

    async def delete_movie(self, input_dto: DeleteMovieCommandDTO) -> None:
        await self._postgres_adapter.delete_movie(input_dto=input_dto)
