from archipy.adapters.base.sqlalchemy.adapters import SQLAlchemyFilterMixin
from archipy.adapters.base.sqlalchemy.ports import AsyncSQLAlchemyPort
from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.errors import AlreadyExistsError, NotFoundError
from archipy.models.types.base_types import FilterOperationType
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import Select

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
from src.models.entities.genre_entity import GenreEntity


class GenrePostgresAdapter(SQLAlchemyFilterMixin):
    def __init__(self, adapter: AsyncPostgresSQLAlchemyAdapter) -> None:
        self._adapter: AsyncSQLAlchemyPort = adapter

    async def create_genre(self, input_dto: CreateGenreCommandDTO) -> CreateGenreResponseDTO:
        genre: GenreEntity = GenreEntity(**input_dto.model_dump())
        try:
            result = await self._adapter.create(entity=genre)
            return CreateGenreResponseDTO.model_validate(obj=result)
        except IntegrityError as exc:
            error_message = str(exc.orig).lower() if exc.orig else ""
            if "unique" in error_message or "duplicate" in error_message:
                raise AlreadyExistsError(resource_type=GenreEntity.__name__) from exc
            raise exc

    async def bulk_create_genre(self, input_dto: BulkCreateGenreCommandDTO) -> BulkCreateGenreResponseDTO:
        results: list[CreateGenreResponseDTO] = []
        for genre_dto in input_dto.genres:
            genre: GenreEntity = GenreEntity(**genre_dto.model_dump())
            try:
                result = await self._adapter.create(entity=genre)
                results.append(CreateGenreResponseDTO.model_validate(obj=result))
            except IntegrityError as exc:
                error_message = str(exc.orig).lower() if exc.orig else ""
                if "unique" in error_message or "duplicate" in error_message:
                    raise AlreadyExistsError(resource_type=GenreEntity.__name__) from exc
                raise exc
        return BulkCreateGenreResponseDTO(genres=results)

    async def get_genre(self, input_dto: GetGenreQueryDTO) -> GetGenreResponseDTO:
        select_query = select(GenreEntity).where(GenreEntity.genre_uuid == input_dto.genre_uuid)
        result = await self._adapter.execute(statement=select_query)
        genre = result.scalar()
        if not genre:
            raise NotFoundError(resource_type=GenreEntity.__name__)
        return GetGenreResponseDTO.model_validate(obj=genre)

    async def search_genres(self, input_dto: SearchGenreQueryDTO) -> SearchGenreResponseDTO:
        query: Select = select(GenreEntity)

        if input_dto.name:
            query = self._apply_filter(
                query=query,
                field=GenreEntity.name,
                value=f"%{input_dto.name}%",
                operation=FilterOperationType.ILIKE,
            )

        genres, total = await self._adapter.execute_search_query(
            query=query,
            entity=GenreEntity,
            sort_info=input_dto.sort_info,
            pagination=input_dto.pagination,
        )

        return SearchGenreResponseDTO(genres=genres, total=total)

    async def update_genre(self, input_dto: UpdateGenreCommandDTO) -> None:
        update_data = input_dto.model_dump(exclude={"genre_uuid"}, exclude_none=True)
        if not update_data:
            return

        update_query = update(GenreEntity).where(GenreEntity.genre_uuid == input_dto.genre_uuid).values(**update_data)

        result = await self._adapter.execute(statement=update_query)
        if result.rowcount == 0:
            raise NotFoundError(resource_type=GenreEntity.__name__)

    async def delete_genre(self, input_dto: DeleteGenreCommandDTO) -> None:
        delete_query = delete(GenreEntity).where(GenreEntity.genre_uuid == input_dto.genre_uuid)
        result = await self._adapter.execute(statement=delete_query)
        if result.rowcount == 0:
            raise NotFoundError(resource_type=GenreEntity.__name__)
