from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator

from src.models.dtos.movie.domain.v1.movie_domain_interface_dtos import (
    BulkCreateMovieInputDTOV1,
    BulkCreateMovieOutputDTOV1,
    CreateMovieInputDTOV1,
    CreateMovieOutputDTOV1,
    DeleteMovieInputDTOV1,
    GetMovieInputDTOV1,
    GetMovieOutputDTOV1,
    SearchMovieInputDTOV1,
    SearchMovieOutputDTOV1,
    UpdateMovieInputDTOV1,
)
from src.models.dtos.movie.repository.movie_repository_interface_dtos import (
    BulkCreateMovieCommandDTO,
    CreateMovieCommandDTO,
    DeleteMovieCommandDTO,
    GetMovieQueryDTO,
    SearchMovieQueryDTO,
    UpdateMovieCommandDTO,
)
from src.repositories.movie.movie_repository import MovieRepository


class MovieLogic:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository: MovieRepository = repository

    @async_postgres_sqlalchemy_atomic_decorator
    async def create_movie(self, input_dto: CreateMovieInputDTOV1) -> CreateMovieOutputDTOV1:
        command: CreateMovieCommandDTO = CreateMovieCommandDTO.model_validate(obj=input_dto.model_dump())
        response = await self._repository.create_movie(input_dto=command)
        return CreateMovieOutputDTOV1.model_validate(obj=response)

    @async_postgres_sqlalchemy_atomic_decorator
    async def bulk_create_movie(self, input_dto: BulkCreateMovieInputDTOV1) -> BulkCreateMovieOutputDTOV1:
        command = BulkCreateMovieCommandDTO(
            movies=[CreateMovieCommandDTO.model_validate(obj=m.model_dump()) for m in input_dto.movies]
        )
        response = await self._repository.bulk_create_movie(input_dto=command)
        return BulkCreateMovieOutputDTOV1(
            movies=[CreateMovieOutputDTOV1.model_validate(obj=m) for m in response.movies]
        )

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_movie(self, input_dto: GetMovieInputDTOV1) -> GetMovieOutputDTOV1:
        query: GetMovieQueryDTO = GetMovieQueryDTO.model_validate(obj=input_dto.model_dump())
        response = await self._repository.get_movie(input_dto=query)
        return GetMovieOutputDTOV1.model_validate(obj=response)

    @async_postgres_sqlalchemy_atomic_decorator
    async def search_movies(self, input_dto: SearchMovieInputDTOV1) -> SearchMovieOutputDTOV1:
        query: SearchMovieQueryDTO = SearchMovieQueryDTO.model_validate(obj=input_dto.model_dump())
        response = await self._repository.search_movies(input_dto=query)
        return SearchMovieOutputDTOV1.model_validate(obj=response)

    @async_postgres_sqlalchemy_atomic_decorator
    async def update_movie(self, input_dto: UpdateMovieInputDTOV1) -> None:
        command: UpdateMovieCommandDTO = UpdateMovieCommandDTO.model_validate(obj=input_dto.model_dump())
        await self._repository.update_movie(input_dto=command)

    @async_postgres_sqlalchemy_atomic_decorator
    async def delete_movie(self, input_dto: DeleteMovieInputDTOV1) -> None:
        command: DeleteMovieCommandDTO = DeleteMovieCommandDTO.model_validate(obj=input_dto.model_dump())
        await self._repository.delete_movie(input_dto=command)
