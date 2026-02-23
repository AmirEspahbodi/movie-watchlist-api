from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator

from src.models.dtos.genre.domain.v1.genre_domain_interface_dtos import (
    BulkCreateGenreInputDTOV1,
    BulkCreateGenreOutputDTOV1,
    CreateGenreInputDTOV1,
    CreateGenreOutputDTOV1,
    DeleteGenreInputDTOV1,
    GetGenreInputDTOV1,
    GetGenreOutputDTOV1,
    SearchGenreInputDTOV1,
    SearchGenreOutputDTOV1,
    UpdateGenreInputDTOV1,
)
from src.models.dtos.genre.repository.genre_repository_interface_dtos import (
    BulkCreateGenreCommandDTO,
    CreateGenreCommandDTO,
    DeleteGenreCommandDTO,
    GetGenreQueryDTO,
    SearchGenreQueryDTO,
    UpdateGenreCommandDTO,
)
from src.repositories.genre.genre_repository import GenreRepository


class GenreLogic:
    def __init__(self, repository: GenreRepository) -> None:
        self._repository: GenreRepository = repository

    @async_postgres_sqlalchemy_atomic_decorator
    async def create_genre(self, input_dto: CreateGenreInputDTOV1) -> CreateGenreOutputDTOV1:
        command: CreateGenreCommandDTO = CreateGenreCommandDTO.model_validate(obj=input_dto.model_dump())
        response = await self._repository.create_genre(input_dto=command)
        return CreateGenreOutputDTOV1.model_validate(obj=response)

    @async_postgres_sqlalchemy_atomic_decorator
    async def bulk_create_genre(self, input_dto: BulkCreateGenreInputDTOV1) -> BulkCreateGenreOutputDTOV1:
        command = BulkCreateGenreCommandDTO(
            genres=[CreateGenreCommandDTO.model_validate(obj=g.model_dump()) for g in input_dto.genres]
        )
        response = await self._repository.bulk_create_genre(input_dto=command)
        return BulkCreateGenreOutputDTOV1(
            genres=[CreateGenreOutputDTOV1.model_validate(obj=g) for g in response.genres]
        )

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_genre(self, input_dto: GetGenreInputDTOV1) -> GetGenreOutputDTOV1:
        query: GetGenreQueryDTO = GetGenreQueryDTO.model_validate(obj=input_dto.model_dump())
        response = await self._repository.get_genre(input_dto=query)
        return GetGenreOutputDTOV1.model_validate(obj=response)

    @async_postgres_sqlalchemy_atomic_decorator
    async def search_genres(self, input_dto: SearchGenreInputDTOV1) -> SearchGenreOutputDTOV1:
        query: SearchGenreQueryDTO = SearchGenreQueryDTO.model_validate(obj=input_dto.model_dump())
        response = await self._repository.search_genres(input_dto=query)
        return SearchGenreOutputDTOV1.model_validate(obj=response)

    @async_postgres_sqlalchemy_atomic_decorator
    async def update_genre(self, input_dto: UpdateGenreInputDTOV1) -> None:
        command: UpdateGenreCommandDTO = UpdateGenreCommandDTO.model_validate(obj=input_dto.model_dump())
        await self._repository.update_genre(input_dto=command)

    @async_postgres_sqlalchemy_atomic_decorator
    async def delete_genre(self, input_dto: DeleteGenreInputDTOV1) -> None:
        command: DeleteGenreCommandDTO = DeleteGenreCommandDTO.model_validate(obj=input_dto.model_dump())
        await self._repository.delete_genre(input_dto=command)
