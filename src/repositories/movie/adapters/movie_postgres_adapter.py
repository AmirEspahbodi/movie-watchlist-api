from archipy.adapters.base.sqlalchemy.adapters import SQLAlchemyFilterMixin
from archipy.adapters.base.sqlalchemy.ports import AsyncSQLAlchemyPort
from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.errors import AlreadyExistsError, NotFoundError
from archipy.models.types.base_types import FilterOperationType
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import Select

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
from src.models.entities.movie_entity import MovieEntity


class MoviePostgresAdapter(SQLAlchemyFilterMixin):
    def __init__(self, adapter: AsyncPostgresSQLAlchemyAdapter) -> None:
        self._adapter: AsyncSQLAlchemyPort = adapter

    async def create_movie(self, input_dto: CreateMovieCommandDTO) -> CreateMovieResponseDTO:
        movie: MovieEntity = MovieEntity(**input_dto.model_dump())
        try:
            result = await self._adapter.create(entity=movie)
            return CreateMovieResponseDTO.model_validate(obj=result)
        except IntegrityError as exc:
            error_message = str(exc.orig).lower() if exc.orig else ""
            if "unique" in error_message or "duplicate" in error_message:
                raise AlreadyExistsError(resource_type=MovieEntity.__name__) from exc
            raise exc

    async def bulk_create_movie(self, input_dto: BulkCreateMovieCommandDTO) -> BulkCreateMovieResponseDTO:
        results: list[CreateMovieResponseDTO] = []
        for movie_dto in input_dto.movies:
            movie: MovieEntity = MovieEntity(**movie_dto.model_dump())
            try:
                result = await self._adapter.create(entity=movie)
                results.append(CreateMovieResponseDTO.model_validate(obj=result))
            except IntegrityError as exc:
                error_message = str(exc.orig).lower() if exc.orig else ""
                if "unique" in error_message or "duplicate" in error_message:
                    raise AlreadyExistsError(resource_type=MovieEntity.__name__) from exc
                raise exc
        return BulkCreateMovieResponseDTO(movies=results)

    async def get_movie(self, input_dto: GetMovieQueryDTO) -> GetMovieResponseDTO:
        select_query = select(MovieEntity).where(MovieEntity.movie_uuid == input_dto.movie_uuid)
        result = await self._adapter.execute(statement=select_query)
        movie = result.scalar()
        if not movie:
            raise NotFoundError(resource_type=MovieEntity.__name__)
        return GetMovieResponseDTO.model_validate(obj=movie)

    async def search_movies(self, input_dto: SearchMovieQueryDTO) -> SearchMovieResponseDTO:
        query: Select = select(MovieEntity)

        if input_dto.title:
            query = self._apply_filter(
                query=query,
                field=MovieEntity.title,
                value=f"%{input_dto.title}%",
                operation=FilterOperationType.ILIKE,
            )

        if input_dto.genre_uuid:
            query = self._apply_filter(
                query=query,
                field=MovieEntity.genre_uuid,
                value=input_dto.genre_uuid,
                operation=FilterOperationType.EQUAL,
            )

        movies, total = await self._adapter.execute_search_query(
            query=query,
            entity=MovieEntity,
            sort_info=input_dto.sort_info,
            pagination=input_dto.pagination,
        )

        return SearchMovieResponseDTO(movies=movies, total=total)

    async def update_movie(self, input_dto: UpdateMovieCommandDTO) -> None:
        update_data = input_dto.model_dump(exclude={"movie_uuid"}, exclude_none=True)
        if not update_data:
            return

        update_query = update(MovieEntity).where(MovieEntity.movie_uuid == input_dto.movie_uuid).values(**update_data)

        result = await self._adapter.execute(statement=update_query)
        if result.rowcount == 0:
            raise NotFoundError(resource_type=MovieEntity.__name__)

    async def delete_movie(self, input_dto: DeleteMovieCommandDTO) -> None:
        delete_query = delete(MovieEntity).where(MovieEntity.movie_uuid == input_dto.movie_uuid)
        result = await self._adapter.execute(statement=delete_query)
        if result.rowcount == 0:
            raise NotFoundError(resource_type=MovieEntity.__name__)
