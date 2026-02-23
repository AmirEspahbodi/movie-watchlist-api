from archipy.adapters.base.sqlalchemy.adapters import SQLAlchemyFilterMixin
from archipy.adapters.base.sqlalchemy.ports import AsyncSQLAlchemyPort
from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.errors import AlreadyExistsError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models.dtos.watch.repository.watch_repository_interface_dtos import (
    CheckWatchExistsQueryDTO,
    CreateWatchCommandDTO,
    CreateWatchResponseDTO,
)
from src.models.entities.user_watch_movie_entity import UserWatchMovieEntity


class WatchPostgresAdapter(SQLAlchemyFilterMixin):
    def __init__(self, adapter: AsyncPostgresSQLAlchemyAdapter) -> None:
        self._adapter: AsyncSQLAlchemyPort = adapter

    async def check_watch_exists(self, input_dto: CheckWatchExistsQueryDTO) -> bool:
        select_query = select(UserWatchMovieEntity).where(
            UserWatchMovieEntity.user_uuid == input_dto.user_uuid,
            UserWatchMovieEntity.movie_uuid == input_dto.movie_uuid,
        )
        result = await self._adapter.execute(statement=select_query)
        return result.scalar() is not None

    async def create_watch(self, input_dto: CreateWatchCommandDTO) -> CreateWatchResponseDTO:
        watch: UserWatchMovieEntity = UserWatchMovieEntity(**input_dto.model_dump())
        try:
            result = await self._adapter.create(entity=watch)
            return CreateWatchResponseDTO.model_validate(obj=result)
        except IntegrityError as exc:
            raise AlreadyExistsError(resource_type=UserWatchMovieEntity.__name__) from exc
